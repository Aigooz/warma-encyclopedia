#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断历史弹幕缓存：按天分解记录数 / 唯一 id / 真正新增，并检查分页排序。"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")


def day_records(d):
    recs = []
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json") or f.endswith(".tmp"):
            continue
        j = json.load(open(os.path.join(d, f), encoding="utf-8"))
        recs.extend(j.get("danmaku") or [])
    return recs


def main():
    bvid = sys.argv[1] if len(sys.argv) > 1 else "BV1D7411t7Be"
    base = os.path.join("danmaku", "history", f"{bvid}.p001")
    days = sorted(x for x in os.listdir(base) if x != "_index")
    seen = set()
    grand = 0
    print(f"{'day':10s} {'recs':>7s} {'uniq':>7s} {'new':>7s}")
    for day in days:
        recs = day_records(os.path.join(base, day))
        ids = [str(r.get("id")) for r in recs]
        uniq = set(ids)
        new = uniq - seen
        grand += len(recs)
        print(f"{day:10s} {len(recs):7d} {len(uniq):7d} {len(new):7d}")
        seen |= uniq
    print("-" * 40)
    print(f"TOTAL recs={grand}  union_unique={len(seen)}")

    # 检查最后一天的分页 send_time 排序与重叠
    last = days[-1]
    d = os.path.join(base, last)
    print(f"\n== {last} 每页 send_time 范围与页间 id 重叠 ==")
    prev_ids = None
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json") or f.endswith(".tmp"):
            continue
        j = json.load(open(os.path.join(d, f), encoding="utf-8"))
        recs = j.get("danmaku") or []
        ids = [str(r.get("id")) for r in recs]
        ts = [r.get("send_time") or 0 for r in recs]
        ov = len(set(ids) & prev_ids) if prev_ids is not None else 0
        if ts:
            import datetime as dt
            fmt = lambda t: dt.datetime.fromtimestamp(t).strftime("%Y-%m-%d")
            print(f"{f} n={len(recs):5d} ts=[{fmt(min(ts))} .. {fmt(max(ts))}] 与上页重叠={ov}")
        else:
            print(f"{f} n=0 error={j.get('error')}")
        prev_ids = set(ids)


main()
