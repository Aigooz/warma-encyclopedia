#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""决定性实验：解析历史 seg.so 的分页元数据与页间关系。"""
import configparser
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path

from bilibili_api.utils.BytesReader import BytesReader

from fetch_history_danmaku import protobuf_danmaku_records


ROOT = Path(__file__).resolve().parents[1]


def load_cookie() -> str:
    parser = configparser.RawConfigParser()
    parser.read(ROOT / "config.ini", encoding="utf-8-sig")
    for section in parser.sections():
        if parser.has_option(section, "cookie"):
            return parser.get(section, "cookie").strip()
    return ""


def fetch_raw(oid: int, date: str, seg: int) -> bytes:
    url = (f"https://api.bilibili.com/x/v2/dm/web/history/seg.so"
           f"?type=1&oid={oid}&date={date}&segment_index={seg}")
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/video/BV1D7411t7Be/",
        "Cookie": load_cookie(),
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def parse_meta(data: bytes) -> dict:
    """解析顶层字段，提取 type-5 (DmSegConfig) 的内容。"""
    reader = BytesReader(data)
    metas = []
    while not reader.has_end():
        type_ = reader.varint() >> 3
        if type_ == 1:
            reader.bytes_string()
        elif type_ == 4:
            reader.bytes_string()
        elif type_ == 5:
            blob = reader.bytes_string()
            r2 = BytesReader(blob)
            fields = {}
            while not r2.has_end():
                t2 = r2.varint() >> 3
                if t2 in (1, 2, 3, 4):
                    fields[t2] = r2.varint()
                elif t2 == 5:
                    fields[t2] = r2.bytes_string().decode("utf-8", "replace")
                else:
                    break
            metas.append(fields)
        elif type_ == 13:
            continue
        else:
            continue
    return {"metas": metas}


def main() -> None:
    oid = 149793525
    for date in ("2026-10-04", "2020-03-31"):
        raws = {}
        for seg in (1, 2, 3):
            raws[seg] = fetch_raw(oid, date, seg)
            time.sleep(0.6)
        print(f"== date={date} ==")
        print("raw equal s1==s2:", raws[1] == raws[2], " s2==s3:", raws[2] == raws[3])
        for seg, raw in raws.items():
            recs = protobuf_danmaku_records(raw)
            ts = [r["send_time"] for r in recs if r.get("send_time")]
            meta = parse_meta(raw)
            desc = all(ts[i] >= ts[i + 1] for i in range(min(len(ts), 200)))
            import datetime as dt
            fmt = lambda t: dt.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M")
            rng = f"[{fmt(min(ts))} .. {fmt(max(ts))}]" if ts else "[]"
            print(f"  s{seg}: n={len(recs)} ts={rng} desc_first200={desc} meta={meta['metas']}")


main()
