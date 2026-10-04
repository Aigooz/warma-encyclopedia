#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性探测：单日期累积窗口抓取（验证 412 状态与 s002 行为）。"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bilibili_api import Credential

from fetch_history_danmaku import fetch_window, load_cookie_from_config, parse_cookie


async def main() -> None:
    bvid, cid = sys.argv[1], int(sys.argv[2])
    day = sys.argv[3]
    ck = parse_cookie(load_cookie_from_config())
    cred = Credential(sessdata=ck.get("SESSDATA"), buvid3=ck.get("buvid3"),
                      bili_jct=ck.get("bili_jct"), dedeuserid=ck.get("DedeUserID"))
    job = {"bvid": bvid, "page": 1, "cid": cid}
    recs = await fetch_window(cred, job, day)
    print("window records:", len(recs))
    if recs:
        ts = sorted(int(r["send_time"]) for r in recs)
        print("range", datetime.fromtimestamp(ts[0]), "->", datetime.fromtimestamp(ts[-1]))


if __name__ == "__main__":
    asyncio.run(main())
