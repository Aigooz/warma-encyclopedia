#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史弹幕抓取（v2.1 按天窗口扫描策略）。

接口实测结论（2026-10）：
    GET x/v2/dm/web/history/seg.so?type=1&oid={cid}&date={YYYY-MM-DD}&segment_index=N
返回"截至该日期 24:00 仍然存活（未被删除/自查）"的弹幕池中**最新的 <=3000 条**，
按 send_time 倒序。segment_index 已实测失效：无论传什么值，服务端都返回页 1 的
拷贝（字节级相同），因此分页不可用，每天只能拿到一个 3000 条的窗口。

关键性质：某条弹幕只要在它发送当天 24:00 仍然存活，就一定位于当天的窗口顶部
（当天比它更晚的弹幕通常少于 3000 条）。因此：

1. 从投稿日起按天扫描：活跃期逐天探测，冷清期步长翻倍跳跃（最多跳 30 天）；
2. 若某次探测的窗口完全落在上次探测点之后（窗口内最老弹幕晚于上次探测日 24:00），
   说明间隔期新增 >= 3000 条、可能有弹幕滑出窗口，立即回填间隔期每一天；
3. 所有结果按（日期,）文件缓存，可断点续跑；
   弹幕 id 去重合并交给 fetch_danmaku.py --aggregate-only。

限速：默认 DANMAKU_PACE=0.7 秒/请求/线程；412 风控自动冷却 600 秒重试。

用法：
    python tools/fetch_history_danmaku.py --limit 3 --workers 1   # 小样本验证
    python tools/fetch_history_danmaku.py --workers 2             # 全量抓取
"""

from __future__ import annotations

import argparse
import asyncio
import configparser
import csv
import json
import os
import random
import sys
import time
from datetime import date, datetime, timedelta
from getpass import getpass
from pathlib import Path
from zoneinfo import ZoneInfo

from bilibili_api import Api, Credential, ResponseCodeException
from bilibili_api import video as bili_video
from bilibili_api.utils.BytesReader import BytesReader

from fetch_danmaku import UA, account_label, bilibili_danmaku_to_record, load_json, now_iso, save_json


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_FILE = ROOT / "registry.json"
CACHE_FILE = ROOT / "tools" / "bili_meta_cache.json"
OUT_DIR = ROOT / "danmaku" / "history"
SUMMARY_FILE = OUT_DIR / "summary.json"
TZ = ZoneInfo("Asia/Shanghai")
PACE = max(0.0, float(os.environ.get("DANMAKU_PACE", "0.7")))
MAX_SKIP = max(1, int(os.environ.get("DANMAKU_MAX_SKIP", "30")))  # 冷清期单次最大跳天数
BACKFILL_MIN_RECORDS = 490  # 接口可能按 500/1000/3000 窗口返回；接近满载即回填
RISK_COOLDOWN = max(60, int(os.environ.get("DANMAKU_RISK_COOLDOWN", "600")))
_RATE_LOCK = asyncio.Lock()
_LAST_REQUEST_AT = 0.0


def parse_cookie(text: str) -> dict[str, str]:
    parts = [item.strip() for item in text.replace("\n", ";").split(";") if "=" in item]
    result = {}
    for item in parts:
        key, value = item.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def load_cookie_from_config() -> str:
    parser = configparser.RawConfigParser()
    parser.read(ROOT / "config.ini", encoding="utf-8-sig")
    for section in parser.sections():
        if parser.has_option(section, "cookie"):
            return parser.get(section, "cookie").strip()
    return ""


def protobuf_danmaku_records(data: bytes) -> list[dict]:
    records: list[dict] = []
    reader = BytesReader(data)
    while not reader.has_end():
        type_ = reader.varint() >> 3
        if type_ == 1:
            dm = bili_video.Danmaku("")
            dm_reader = BytesReader(reader.bytes_string())
            while not dm_reader.has_end():
                field = dm_reader.varint() >> 3
                if field == 1:
                    dm.id_ = dm_reader.varint()
                elif field == 2:
                    dm.dm_time = dm_reader.varint() / 1000
                elif field == 3:
                    dm.mode = dm_reader.varint()
                elif field == 4:
                    dm.font_size = dm_reader.varint()
                elif field == 5:
                    color = dm_reader.varint()
                    dm.color = "special" if color == 60001 else hex(color)[2:]
                elif field == 6:
                    dm.crc32_id = dm_reader.string()
                elif field == 7:
                    dm.text = dm_reader.string()
                elif field == 8:
                    dm.send_time = dm_reader.varint()
                elif field == 9:
                    dm.weight = dm_reader.varint()
                elif field == 10:
                    dm.action = str(dm_reader.string())
                elif field == 11:
                    dm.pool = dm_reader.varint()
                elif field == 12:
                    dm.id_str = dm_reader.string()
                elif field == 13:
                    dm.attr = dm_reader.varint()
                elif field == 14:
                    dm.uid = dm_reader.varint()
                elif field in (15, 20, 21, 22):
                    if field == 15:
                        dm_reader.varint()
                    else:
                        dm_reader.bytes_string()
                elif field in (25, 26):
                    dm_reader.varint()
                else:
                    break
            rec = bilibili_danmaku_to_record(dm)
            if rec:
                rec["source"] = ["history"]
                records.append(rec)
        elif type_ == 4:
            reader.bytes_string()
        elif type_ == 5:
            reader.varint()
            reader.varint()
            reader.varint()
            reader.bytes_string()
        elif type_ == 13:
            continue
        else:
            continue
    return records


def month_range(start: date, end: date) -> list[str]:
    months = []
    current = start.replace(day=1)
    while current <= end:
        months.append(current.strftime("%Y-%m"))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return months


def month_last_day(month: str, today: date) -> date:
    year, mon = (int(x) for x in month.split("-"))
    if year == today.year and mon == today.month:
        return today
    if mon == 12:
        return date(year, 12, 31)
    return date(year, mon + 1, 1) - timedelta(days=1)


def history_dir(bvid: str, page: int) -> Path:
    return OUT_DIR / f"{bvid}.p{page:03d}"


def segment_file(bvid: str, page: int, day: str, segment_index: int) -> Path:
    d = history_dir(bvid, page) / day.replace("-", "")
    d.mkdir(parents=True, exist_ok=True)
    return d / f"s{segment_index:03d}.json"


async def request_bytes(
    api: dict,
    params: dict,
    credential: Credential,
    headers: dict | None = None,
    retries: int = 5,
    request_timeout: float = 45.0,
) -> bytes | None:
    """请求 seg.so；412 风控冷却 600 秒重试，404 返回 None，其余异常重试后抛出。
    外层 asyncio.wait_for 兜底超时，防止 B 站 tarpit 导致请求永久挂起。"""
    global _LAST_REQUEST_AT
    last_exc: Exception | None = None
    async with _RATE_LOCK:
        for attempt in range(retries):
            try:
                if PACE:
                    wait = _LAST_REQUEST_AT + random.uniform(PACE, PACE * 1.25) - time.monotonic()
                    if wait > 0:
                        await asyncio.sleep(wait)
                request = Api(
                    url=api["url"],
                    method=api["method"],
                    verify=True,
                    credential=credential,
                    headers=headers or {},
                ).update_params(**params).request(byte=True)
                result = await asyncio.wait_for(request, timeout=request_timeout)
                if PACE:
                    _LAST_REQUEST_AT = time.monotonic()
                # B 站历史弹幕接口可能返回 HTTP 200 + JSON code=-702（请求频率过高）。
                # 这绝不能当作空窗口缓存，必须冷却后重试。
                if result.startswith(b"{"):
                    try:
                        payload = json.loads(result)
                        code = int(payload.get("code") or 0)
                    except Exception:
                        code = 0
                    if code == -702:
                        print(f"  [-702] 触发历史弹幕限频，冷却 {RISK_COOLDOWN} 秒后重试（第 {attempt + 1}/{retries} 次）...", flush=True)
                        last_exc = RuntimeError("bilibili history API rate limited (-702)")
                        await asyncio.sleep(RISK_COOLDOWN)
                        continue
                    if code != 0:
                        if code in (-404, 404):
                            return None
                        last_exc = RuntimeError(f"history API JSON error {code}: {payload.get('message')}")
                        await asyncio.sleep(5 * (attempt + 1))
                        continue
                return result
            except ResponseCodeException as exc:
                last_exc = exc
                code = getattr(exc, "code", None)
                if code in (404, -404):
                    return None
                if code == 412:
                    print(f"  [412] 触发风控，冷却 {RISK_COOLDOWN} 秒后重试（第 {attempt + 1}/{retries} 次）...", flush=True)
                    await asyncio.sleep(RISK_COOLDOWN)
                    continue
                await asyncio.sleep(2 * (attempt + 1))
            except (asyncio.TimeoutError, TimeoutError):
                last_exc = TimeoutError(f"request timeout after {request_timeout}s")
                print(f"  [timeout] 请求超过 {request_timeout}s，重试（第 {attempt + 1}/{retries} 次）...", flush=True)
                await asyncio.sleep(5 * (attempt + 1))
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                await asyncio.sleep(2 * (attempt + 1))
        raise last_exc  # type: ignore[misc]


def read_cached_page(bvid: str, page: int, day: str, segment_index: int) -> list[dict] | None:
    """读取单个 segment 分页缓存；未缓存返回 None，已缓存（含空页/404）返回记录列表。"""
    cached = load_json(segment_file(bvid, page, day, segment_index), None)
    if not isinstance(cached, dict):
        return None
    error = cached.get("error")
    if error in ("not_found", "danmaku_closed"):
        return []
    if error is None and isinstance(cached.get("danmaku"), list):
        return cached["danmaku"]
    return None


async def fetch_day(credential: Credential, job: dict, day: str) -> list[dict]:
    """抓取某日历史弹幕窗口（页 1）并写入缓存；命中缓存不发请求。
    服务端对 segment_index>1 返回页 1 拷贝，故只请求页 1。"""
    cached = read_cached_page(job["bvid"], job["page"], day, 1)
    if cached is not None:
        return cached
    api = bili_video.API["danmaku"]["get_history_danmaku"]
    params = {"oid": job["cid"], "type": 1, "date": day, "segment_index": 1}
    raw = await request_bytes(api, params, credential, headers={
        "User-Agent": UA,
        "Referer": f"https://www.bilibili.com/video/{job['bvid']}/",
        "Origin": "https://www.bilibili.com",
    })
    if raw is None:
        got: list[dict] = []
        error = "not_found"
    elif raw == b"\x10\x01":
        got = []
        error = "danmaku_closed"
    else:
        got = protobuf_danmaku_records(raw)
        error = None
    save_json(segment_file(job["bvid"], job["page"], day, 1), {
        "version": 2,
        "bvid": job["bvid"],
        "aid": job.get("aid"),
        "page": job["page"],
        "cid": job["cid"],
        "date": day,
        "segment_index": 1,
        "fetched_at": now_iso(),
        "danmaku": got,
        "error": error,
    })
    return got


def day_end_ts(d: date) -> int:
    """某日 23:59:59（Asia/Shanghai）的 unix 时间戳。"""
    return int(datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=TZ).timestamp())


def load_fetched_counts() -> dict[str, int]:
    """从 per_video_summary.csv 读取每个 BV 已抓取的弹幕数。"""
    result: dict[str, int] = {}
    path = ROOT / "danmaku" / "per_video_summary.csv"
    if not path.exists():
        return result
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        for row in csv.DictReader(fp):
            try:
                result[row.get("bvid")] = int(row.get("danmaku_count") or 0)
            except (TypeError, ValueError):
                continue
    return result


def build_jobs(limit: int, accounts: set[str] | None, order: str = "deficit") -> list[dict]:
    registry = load_json(REGISTRY_FILE, {})
    cache = load_json(CACHE_FILE, {})
    fetched = load_fetched_counts() if order == "deficit" else {}
    jobs = []
    seen = set()
    for row in registry.get("videos", []):
        bvid = row.get("bvid")
        account = account_label(row.get("account") or "")
        if not bvid or bvid in seen or (accounts and account not in accounts):
            continue
        seen.add(bvid)
        info = cache.get(bvid)
        if not isinstance(info, dict):
            continue
        pubdate = int(info.get("pubdate") or 0)
        if not pubdate:
            continue
        for page in info.get("pages") or []:
            cid = page.get("cid")
            if not cid:
                continue
            jobs.append({
                "bvid": bvid,
                "aid": info.get("aid") or row.get("aid"),
                "page": int(page.get("page") or 1),
                "cid": int(cid),
                "start": datetime.fromtimestamp(pubdate, TZ).date(),
                "pub_ts": pubdate,
                "account": account,
                "deficit": int((info.get("stat") or {}).get("danmaku") or 0) - fetched.get(bvid, 0),
            })
    if order == "deficit":
        jobs.sort(key=lambda j: (-j["deficit"], j["bvid"], j["page"]))
    if limit > 0:
        selected: list[str] = []
        for job in jobs:
            if job["bvid"] not in selected:
                selected.append(job["bvid"])
            if len(selected) >= limit:
                break
        jobs = [job for job in jobs if job["bvid"] in selected]
    return jobs


async def scan_page(
    credential: Credential,
    job: dict,
    today: date,
    state: dict,
) -> None:
    """对一个分P执行按天窗口扫描：
    活跃期逐天、冷清期步长翻倍；窗口越界（完全越过上次探测点）时回填间隔期。"""
    seen: set[str] = set()
    step = 1
    current = job["start"]
    prev: date | None = None
    while current <= today:
        day = current.isoformat()
        records = await fetch_day(credential, job, day)
        if state["abort"]:
            return
        state["fetched"] += 1
        ids = {str(r.get("id")) for r in records}
        new_count = len(ids - seen)
        seen |= ids
        state["rec"] += new_count

        # 回填判定：窗口内最老弹幕晚于上次探测日 24:00 => 间隔期新增过多，可能有
        # 弹幕在间隔期内滑出 3000 条窗口；回填间隔期每一天，找回滑出前的记录。
        total_new = new_count
        ts = [int(r.get("send_time") or 0) for r in records if r.get("send_time")]
        gap_days = (current - prev).days - 1 if prev is not None else 0
        if prev is not None and gap_days > 0 and ts and len(records) >= BACKFILL_MIN_RECORDS \
                and min(ts) > day_end_ts(prev):
            for k in range(1, gap_days + 1):
                gap_day = (prev + timedelta(days=k)).isoformat()
                gap_records = await fetch_day(credential, job, gap_day)
                if state["abort"]:
                    return
                state["fetched"] += 1
                gap_ids = {str(r.get("id")) for r in gap_records}
                gap_new = len(gap_ids - seen)
                total_new += gap_new
                seen |= gap_ids
                state["rec"] += gap_new

        step = 1 if total_new > 0 else min(step * 2, MAX_SKIP)
        if state["fetched"] % 100 == 0:
            print(f"  [进度] 已请求 {state['fetched']} 次，新增记录 {state['rec']}", flush=True)
        prev = current
        current = current + timedelta(days=step)
    state["pages_done"] += 1


async def worker_loop(queue: asyncio.Queue, credential: Credential, today: date, state: dict) -> None:
    while True:
        try:
            job, index, total = await queue.get()
        except asyncio.CancelledError:
            raise
        try:
            await scan_page(credential, job, today, state)
            print(f"[页 {index}/{total}] {job['bvid']} p{job['page']} 完成 "
                  f"(累计请求 {state['fetched']}，新增记录 {state['rec']})", flush=True)
        except Exception as exc:  # noqa: BLE001
            state["err"] += 1
            if getattr(exc, "code", None) == 412:
                state["abort"] = True
            print(f"[页 {index}/{total}] {job['bvid']} p{job['page']} 失败：{exc!r}", flush=True)
        finally:
            queue.task_done()


async def main_async(args) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    cookie_text = os.environ.get("BILI_COOKIE", "").strip()
    if not cookie_text:
        cookie_text = load_cookie_from_config()
    if not cookie_text and not args.no_prompt:
        print("请粘贴 B 站 Cookie（含 SESSDATA）后回车：")
        cookie_text = getpass("").strip()
    if not cookie_text:
        raise RuntimeError("缺少 BILI_COOKIE 或交互输入；历史弹幕需要登录后抓取。")
    cookies = parse_cookie(cookie_text)
    if "SESSDATA" not in cookies:
        raise RuntimeError("Cookie 缺少字段：SESSDATA")
    credential = Credential(
        sessdata=cookies.get("SESSDATA"),
        buvid3=cookies.get("buvid3"),
        bili_jct=cookies.get("bili_jct"),
        dedeuserid=cookies.get("DedeUserID"),
    )
    if not await credential.check_valid():
        raise RuntimeError("B 站 Cookie 已失效，请更新 config.ini 中的 Cookie。")

    jobs = build_jobs(args.limit, set(args.accounts) if args.accounts else None, order=args.order)
    today = datetime.now(TZ).date()
    print(f"准备抓取 {len(jobs)} 个分P（{args.order} 顺序），截至 {today.isoformat()}。", flush=True)
    queue: asyncio.Queue = asyncio.Queue(maxsize=args.workers * 4)
    state = {"fetched": 0, "rec": 0, "err": 0, "pages_done": 0, "abort": False}
    started = time.time()
    total = len(jobs)
    workers = [asyncio.create_task(worker_loop(queue, credential, today, state)) for _ in range(args.workers)]
    for index, job in enumerate(jobs, 1):
        if state["abort"]:
            break
        while True:
            try:
                queue.put_nowait((job, index, total))
                break
            except asyncio.QueueFull:
                if state["abort"]:
                    break
                await asyncio.sleep(0.5)
        if state["abort"]:
            break
    await queue.join()
    for task in workers:
        task.cancel()
    await asyncio.gather(*workers, return_exceptions=True)
    summary = {
        "fetched_at": now_iso(),
        "pages": total,
        "pages_done": state["pages_done"],
        "requests": state["fetched"],
        "history_records": state["rec"],
        "errors": state["err"],
        "aborted": bool(state["abort"]),
        "elapsed_seconds": round(time.time() - started, 1),
    }
    save_json(SUMMARY_FILE, summary)
    print("历史弹幕抓取完成：", json.dumps(summary, ensure_ascii=False), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="按天窗口扫描抓取 B 站历史弹幕")
    parser.add_argument("--limit", type=int, default=0, help="只抓前 N 个 BV（0 表示全部）")
    parser.add_argument("--workers", type=int, default=2, help="并发分P数（默认 2）")
    parser.add_argument("--accounts", nargs="*", choices=["主号", "小号"], help="只抓指定账号")
    parser.add_argument("--order", choices=["deficit", "registry"], default="deficit",
                        help="抓取顺序：deficit=按弹幕亏空从大到小（默认），registry=按登记表顺序")
    parser.add_argument("--no-prompt", action="store_true", help="禁止交互输入，只使用 BILI_COOKIE")
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
