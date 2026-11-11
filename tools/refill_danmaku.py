# -*- coding: utf-8 -*-
"""轻量补齐缺失视频的弹幕（只用标准库，抓 XML 弹幕池）。

正式全量抓取仍是 `tools/fetch_danmaku.py`（依赖 bilibili_api / httpx）；
本脚本用于在小缺口时快速回填，输出与正式脚本一致的 raw 结构（version=3）。

用法：python tools/refill_danmaku.py [--repo nujiu]
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
import zlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPOS = {
    "warma": Path(r"F:\沃怒百科\warma百科\warma-encyclopedia"),
    "nujiu": Path(r"F:\沃怒百科\怒九百科\怒九百科"),
}
TZ = timezone(timedelta(hours=8))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")


def fetch(url: str, referer: str) -> bytes:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Referer": referer,
        "Origin": "https://www.bilibili.com",
        "Accept-Encoding": "gzip",
    })
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw = resp.read()
        encoding = (resp.headers.get("Content-Encoding") or "").lower()
        if encoding == "gzip":
            raw = gzip.decompress(raw)
        elif encoding == "deflate":
            # B 站弹幕 CDN 返回的是 raw deflate（无 zlib 头）。
            try:
                raw = zlib.decompress(raw, -15)
            except zlib.error:
                raw = zlib.decompress(raw)
        return raw


def parse_xml(raw: bytes) -> list:
    root = ET.fromstring(raw)
    out = []
    for node in root.findall("./d"):
        fields = (node.attrib.get("p") or "").split(",")
        while len(fields) < 8:
            fields.append("")
        try:
            out.append({
                "id": fields[7],
                "progress": round(float(fields[0] or 0), 3),
                "mode": int(fields[1] or 1),
                "font_size": int(fields[2] or 25),
                "color": int(fields[3] or 16777215),
                "send_time": int(float(fields[4] or 0)),
                "pool": int(fields[5] or 0),
                "crc32_id": fields[6],
                "weight": 0, "action": 0, "attr": 0,
                "content": node.text or "",
                "source": ["xml"],
            })
        except Exception:
            continue
    return out


def refill(root: Path) -> None:
    sys.path.insert(0, str(root / "tools"))
    import bili_api
    raw_dir = root / "danmaku" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    registry = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    meta = json.loads((root / "tools" / "bili_meta_cache.json").read_text(encoding="utf-8"))
    missing = []
    for row in registry.get("videos") or []:
        bvid = row.get("bvid")
        if not bvid:
            continue
        if not (raw_dir / f"{bvid}.p001.json").exists():
            missing.append(row)
    print(f"[{root.name}] 缺弹幕视频 {len(missing)} 条", flush=True)
    for row in missing:
        bvid = row["bvid"]
        info = meta.get(bvid) or {}
        pages = info.get("pages") or []
        if not pages:
            try:
                pages = bili_api.get_video_info(bvid).get("pages") or []
            except Exception as exc:
                print(f"  ! {bvid} 无法取分P {exc}", flush=True)
                continue
        total = 0
        for page in pages:
            cid = page.get("cid")
            page_no = int(page.get("page") or 1)
            out_file = raw_dir / f"{bvid}.p{page_no:03d}.json"
            if not cid or out_file.exists():
                continue
            try:
                records = parse_xml(fetch(f"https://comment.bilibili.com/{cid}.xml",
                                          f"https://www.bilibili.com/video/{bvid}/"))
            except Exception as exc:
                print(f"  ! {bvid} p{page_no} {type(exc).__name__}: {str(exc)[:70]}", flush=True)
                continue
            payload = {
                "version": 3, "bvid": bvid, "aid": info.get("aid"),
                "cid": cid, "page": page_no,
                "part": page.get("part"), "title": row.get("title"),
                "date": row.get("date"),
                "account": "主号" if "主号" in (row.get("account") or "") else "小号",
                "danmaku": records,
                "source_counts": {"xml": len(records), "seg": 0},
            }
            out_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            total += len(records)
            print(f"  + {bvid} p{page_no} {len(records)} 条", flush=True)
            time.sleep(0.4)
        if total == 0:
            print(f"  = {bvid} 无可抓弹幕", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", choices=list(REPOS), default=None)
    args = parser.parse_args()
    for name in ([args.repo] if args.repo else list(REPOS)):
        refill(REPOS[name])


if __name__ == "__main__":
    main()
