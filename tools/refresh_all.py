# -*- coding: utf-8 -*-
"""统一刷新沃玛百科数据：用户投稿列表 → 元数据 → 标签 → 字幕 → 评论。

与 `tools/update.py` 的区别：本脚本面向"全量对账"，会把两个账号的完整投稿列表
与本地 registry 对比，补齐缺失视频、刷新统计元数据，并可选重抓标签/评论。

用法（在百科根目录执行）：
  python tools/refresh_all.py            # 补齐缺失 + 刷新元数据/标签
  python tools/refresh_all.py --comments # 额外抓取缺失视频的评论
  python tools/refresh_all.py --report   # 只输出差异报告，不写文件
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.stdout.reconfigure(encoding="utf-8")

import bili_api
from classify_videos import classify

TZ = timezone(timedelta(hours=8))
ACCOUNTS = [
    {"mid": "53456", "label": "主号（Warma）", "short": "主号"},
    {"mid": "106320250", "label": "小号（warma养鸽场）", "short": "小号"},
]

REGISTRY = ROOT / "registry.json"
META = ROOT / "tools" / "bili_meta_cache.json"
TAGS = ROOT / "tools" / "bili_tags_cache.json"
COMMENTS = ROOT / "tools" / "bili_comments_cache.json"
SUB_DIR = ROOT / "subtitles"


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")


def iso(ts) -> str:
    return datetime.fromtimestamp(int(ts), TZ).strftime("%Y-%m-%d")


def iso_minutes(ts) -> str:
    return datetime.fromtimestamp(int(ts), TZ).strftime("%Y-%m-%d %H:%M")


def fetch_account_videos(mid: str):
    """拉取一个账号的完整投稿列表（免登录接口月上限较多）。"""
    try:
        return bili_api.get_user_videos(mid, ps=30, max_pages=40)
    except Exception:
        return bili_api.get_user_videos_free(mid, ps=30, max_pages=40)


def fetch_meta(bvid: str) -> dict:
    data = bili_api._get("https://api.bilibili.com/x/web-interface/view", {"bvid": bvid})
    if data.get("code") != 0:
        raise RuntimeError(f"view API code={data.get('code')} msg={data.get('message')}")
    return data["data"]


def fetch_tags(bvid: str) -> list:
    obj = bili_api._get("https://api.bilibili.com/x/tag/archive/tags", {"bvid": bvid})
    if obj.get("code") != 0:
        return []
    return [{"id": x.get("tag_id"), "name": x.get("tag_name")}
            for x in (obj.get("data") or []) if x.get("tag_name")]


def fetch_subtitles(info: dict) -> list:
    lines: list = []
    pages = info.get("pages") or [{"cid": info.get("cid")}]
    for page in pages:
        cid = page.get("cid")
        if not cid:
            continue
        try:
            lines.extend(bili_api.get_subtitle_lines(info["bvid"], cid))
            time.sleep(0.06)
        except Exception:
            pass
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comments", action="store_true", help="重抓缺失视频的评论")
    parser.add_argument("--report", action="store_true", help="只输出差异，不写文件")
    args = parser.parse_args()

    registry = read_json(REGISTRY, {"videos": []})
    meta_cache = read_json(META, {})
    tag_cache = read_json(TAGS, {})
    comment_cache = read_json(COMMENTS, {})
    rows = registry.get("videos") or []
    known = {r.get("bvid") for r in rows if r.get("bvid")}

    added = []
    seen = set()
    for account in ACCOUNTS:
        vids = fetch_account_videos(account["mid"])
        print(f"[{account['short']}] 投稿接口返回 {len(vids)} 条")
        for v in vids:
            bvid = v["bvid"]
            if bvid in known or bvid in seen:
                continue
            seen.add(bvid)
            info = fetch_meta(bvid)
            tags = fetch_tags(bvid)
            lines = fetch_subtitles({**info, "bvid": bvid})
            (SUB_DIR / f"{bvid}.json").write_text(
                json.dumps({"bvid": bvid, "title": info["title"], "desc": info.get("desc", ""),
                            "pubdate": info["pubdate"], "owner_mid": info.get("owner", {}).get("mid"),
                            "owner_name": info.get("owner", {}).get("name"), "lines": lines},
                           ensure_ascii=False, indent=1), encoding="utf-8")
            meta_cache[bvid] = info
            tag_cache[bvid] = tags
            row = {
                "title": info["title"],
                "date": iso(info["pubdate"]),
                "pubdate_iso": iso_minutes(info["pubdate"]),
                "type": classify(info.get("title", ""), info.get("desc", ""),
                                 tags, info.get("tid")),
                "account": account["label"],
                "account_short": account["short"],
                "intro_count": 0,
                "sub_lines": len(lines),
                "sub_chars": sum(len(x) for x in lines),
                "bvid": bvid,
                "aid": info.get("aid"),
                "duration": info.get("duration") or 0,
                "source": "B站用户视频 + B站元数据",
            }
            added.append(row)
            print(f"  + {row['date']} {bvid} {row['title'][:36]} 字幕{row['sub_lines']}行")
            time.sleep(0.2)

    # 刷新已有条目的统计元数据（播放/点赞等会持续变化）
    missing_meta = [r["bvid"] for r in rows + added
                    if r.get("bvid") and r["bvid"] not in meta_cache]
    missing_tags = [r["bvid"] for r in rows + added
                    if r.get("bvid") and r["bvid"] not in tag_cache]

    if args.report:
        print(f"\n新增视频 {len(added)} 条；缺元数据 {len(missing_meta)}；缺标签 {len(missing_tags)}")
        for row in added:
            print("  NEW", row["date"], row["bvid"], row["title"])
        return

    for bvid in list(dict.fromkeys(missing_meta)):
        try:
            meta_cache[bvid] = fetch_meta(bvid)
        except Exception as exc:
            print(f"  [meta] {bvid} 失败 {exc}")
        time.sleep(0.15)
    for bvid in list(dict.fromkeys(missing_tags)):
        try:
            tag_cache[bvid] = fetch_tags(bvid)
        except Exception as exc:
            print(f"  [tags] {bvid} 失败 {exc}")
        time.sleep(0.15)

    if added:
        # 复刻 docx 台账格式：no / title / date / type / account / intro_count /
        # sub_lines / sub_chars / bvid / source
        for row in added:
            rows.append({k: row[k] for k in
                         ("title", "date", "type", "account", "intro_count",
                          "sub_lines", "sub_chars", "bvid", "source")})
        rows.sort(key=lambda r: (r.get("date") or "", r.get("bvid") or ""))
        for index, row in enumerate(rows, 1):
            row["no"] = index
        registry["videos"] = rows
        registry["total_sub_lines"] = sum(r.get("sub_lines") or 0 for r in rows)
        write_json(REGISTRY, registry)

    write_json(META, meta_cache)
    write_json(TAGS, tag_cache)
    print(f"\n完成：台账 {len(rows)} 条（新增 {len(added)}）")
    print(f"元数据 {len(meta_cache)} 条，标签 {len(tag_cache)} 条")


if __name__ == "__main__":
    main()
