#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""估算历史弹幕补抓工作量。"""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")
ROOT = Path(__file__).resolve().parents[1]
registry = json.load(open(ROOT / "registry.json", encoding="utf-8"))["videos"]
cache = json.load(open(ROOT / "tools" / "bili_meta_cache.json", encoding="utf-8"))
today = datetime.now(TZ).date()
hist = ROOT / "danmaku" / "history"
total_idx = 0
total_seg = 0
n_pages = 0
videos = {}
seen = set()
for row in registry:
    bv = row.get("bvid")
    if not bv or bv in seen:
        continue
    seen.add(bv)
    info = cache.get(bv)
    if not isinstance(info, dict):
        continue
    pub = int(info.get("pubdate") or 0)
    if not pub:
        continue
    start = datetime.fromtimestamp(pub, TZ).date()
    total_danmaku = int((info.get("stat") or {}).get("danmaku") or 0)
    for pg in info.get("pages") or []:
        cid = pg.get("cid")
        if not cid:
            continue
        n_pages += 1
        dur = int(pg.get("duration") or info.get("duration") or 0)
        segc = max(1, (dur + 359) // 360)
        months = (today.year * 12 + today.month) - (start.year * 12 + start.month) + 1
        page_no = int(pg.get("page") or 1)
        cached = 0
        idir = hist / f"{bv}.p{page_no:03d}" / "_index"
        if idir.exists():
            cached = len(list(idir.glob("*.json")))
        total_idx += max(0, months - cached)
        days = 0
        if idir.exists():
            for f in idir.glob("*.json"):
                try:
                    d = json.load(open(f, encoding="utf-8"))
                    days += len(d.get("dates") or [])
                except Exception:
                    pass
        segfiles = len(list(hist.glob(f"{bv}.p*/2*/s*.json")))
        total_seg += max(0, days * segc - segfiles)
        v = videos.setdefault(bv, {"stat": total_danmaku, "segs": 0, "days": 0,
                                   "title": (info.get("title") or "")[:24]})
        v["segs"] += days * segc
        v["days"] += days

print("pages", n_pages, "uncached index reqs", total_idx,
      "uncached seg reqs", total_seg, "total", total_idx + total_seg)
top = sorted(videos.items(), key=lambda kv: -kv[1]["stat"])[:12]
for bv, v in top:
    print(bv, v["stat"], "days", v["days"], "segs", v["segs"], v["title"])
