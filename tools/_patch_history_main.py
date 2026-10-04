#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性脚本：重写 fetch_history_danmaku.py 的 worker_loop 与 main_async。"""
from pathlib import Path

path = Path(__file__).resolve().parent / "fetch_history_danmaku.py"
text = path.read_text(encoding="utf-8")

start = text.index("async def worker_loop")
end = text.index("def main(")

new_section = '''async def worker_loop(
    queue: asyncio.Queue,
    credential: Credential,
    state: dict,
    errors: list[dict],
) -> None:
    while True:
        try:
            kind, job, month, day, segment_index = await queue.get()
        except asyncio.CancelledError:
            raise
        try:
            if kind == "index":
                out = index_file(job["bvid"], job["page"], month)
                await fetch_month_index(
                    bili_video.Video(bvid=job["bvid"], credential=credential),
                    credential, job["cid"], month, out,
                )
                state["idx"] += 1
                state["b412"] = 0
            else:
                out = segment_file(job["bvid"], job["page"], day, segment_index)
                payload = await fetch_segment(
                    bili_video.Video(bvid=job["bvid"], credential=credential),
                    credential, job, day, segment_index, out,
                )
                state["seg"] += 1
                state["rec"] += len(payload.get("danmaku", []))
                state["b412"] = 0
        except ResponseCodeException as exc:
            state["err"] += 1
            if getattr(exc, "code", None) == 412:
                state["b412"] += 1
                if state["b412"] >= 15:
                    state["abort"] = True
            else:
                state["b412"] = 0
            if len(errors) < 200:
                errors.append({"kind": kind, "bvid": job["bvid"], "month": month,
                               "day": day, "segment": segment_index, "error": repr(exc)})
        except Exception as exc:
            state["err"] += 1
            state["b412"] = 0
            if len(errors) < 200:
                errors.append({"kind": kind, "bvid": job["bvid"], "month": month,
                               "day": day, "segment": segment_index, "error": repr(exc)})
        finally:
            queue.task_done()


async def put_checked(queue: asyncio.Queue, item: tuple, state: dict) -> bool:
    """入队；若熔断触发则返回 False。"""
    while True:
        if state["abort"]:
            return False
        try:
            queue.put_nowait(item)
            return True
        except asyncio.QueueFull:
            await asyncio.sleep(0.2)


async def monitor(state: dict, started: float, stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=60)
        except asyncio.TimeoutError:
            pass
        elapsed = time.time() - started
        print(f"[进度 {elapsed:.0f}s] index={state['idx']} seg={state['seg']} "
              f"records={state['rec']} errors={state['err']} b412={state['b412']}", flush=True)


async def main_async(args) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    cookie_text = os.environ.get("BILI_COOKIE", "").strip()
    if not cookie_text:
        cookie_text = load_cookie_from_config()
    if not cookie_text and not args.no_prompt:
        print("请粘贴完整 B 站 Cookie（包含 SESSDATA），输入后按 Enter：")
        cookie_text = getpass("").strip()
    if not cookie_text:
        raise RuntimeError("缺少 BILI_COOKIE 或交互输入；历史弹幕必须登录后才能抓取。")
    cookies = parse_cookie(cookie_text)
    required = {"SESSDATA"}
    if not required <= cookies.keys():
        raise RuntimeError(f"Cookie 缺少字段：{', '.join(sorted(required - cookies.keys()))}")
    credential = Credential(
        sessdata=cookies.get("SESSDATA"),
        buvid3=cookies.get("buvid3"),
        bili_jct=cookies.get("bili_jct"),
        dedeuserid=cookies.get("DedeUserID"),
    )
    if not await credential.check_valid():
        raise RuntimeError("B 站 Cookie 已失效，请重新导出新的 Cookie。")

    jobs = await build_jobs(args.limit, set(args.accounts) if args.accounts else None, order=args.order)
    today = datetime.now(TZ).date()
    print(f"准备补抓 {len(jobs)} 个分P；月份范围从发布月到 {today.strftime('%Y-%m')}。", flush=True)
    queue: asyncio.Queue = asyncio.Queue(maxsize=args.workers * 8)
    state = {"idx": 0, "seg": 0, "rec": 0, "err": 0, "b412": 0, "abort": False}
    errors: list[dict] = []
    started = time.time()
    stop = asyncio.Event()
    mon = asyncio.create_task(monitor(state, started, stop))
    workers = [asyncio.create_task(worker_loop(queue, credential, state, errors))
               for _ in range(args.workers)]

    def months_of(job: dict) -> list[str]:
        months = month_range(job["start"], today)
        if args.max_months > 0:
            return months[-args.max_months:]
        return months

    # 阶段一：并行抓取所有月份的历史弹幕日期索引（已缓存的自动跳过）。
    aborted = False
    for job in jobs:
        for month in months_of(job):
            cached = load_json(index_file(job["bvid"], job["page"], month))
            if isinstance(cached, dict) and cached.get("version") == 1:
                continue
            if not await put_checked(queue, ("index", job, month, None, None), state):
                aborted = True
                break
        if aborted:
            break
    await queue.join()
    print(f"阶段一完成：index={state['idx']} errors={state['err']} aborted={state['abort']}", flush=True)

    # 阶段二：读取索引缓存，并行抓取各日期的分段弹幕（已缓存的自动跳过）。
    if not state["abort"]:
        for job in jobs:
            for month in months_of(job):
                cached = load_json(index_file(job["bvid"], job["page"], month))
                if not isinstance(cached, dict):
                    continue
                for day in (cached.get("dates") or [])[:args.max_dates_per_month or None]:
                    for segment_index in range(1, job["segment_count"] + 1):
                        seg = load_json(segment_file(job["bvid"], job["page"], day, segment_index))
                        if isinstance(seg, dict) and seg.get("version") == 1:
                            continue
                        if not await put_checked(queue, ("segment", job, None, day, segment_index), state):
                            aborted = True
                            break
                    if aborted:
                        break
                if aborted:
                    break
            if aborted:
                break
        await queue.join()
    print(f"阶段二完成：seg={state['seg']} records={state['rec']} errors={state['err']} aborted={state['abort']}", flush=True)

    stop.set()
    mon.cancel()
    for task in workers:
        task.cancel()
    await asyncio.gather(*workers, return_exceptions=True)
    summary = {
        "fetched_at": now_iso(),
        "jobs": len(jobs),
        "index_requests": state["idx"],
        "segment_requests": state["seg"],
        "history_records": state["rec"],
        "errors": len(errors),
        "aborted": bool(state["abort"]),
        "elapsed_seconds": round(time.time() - started, 1),
    }
    save_json(SUMMARY_FILE, summary)
    print("历史弹幕补抓完成：", json.dumps(summary, ensure_ascii=False), flush=True)
    if errors:
        print("最近错误示例：", json.dumps(errors[-3:], ensure_ascii=False), flush=True)


'''

path.write_text(text[:start] + new_section + text[end:], encoding="utf-8")
print("patched", path)
