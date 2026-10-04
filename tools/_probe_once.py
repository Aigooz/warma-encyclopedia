#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性诊断：带超时请求一次历史弹幕 seg.so，打印状态与耗时。"""
import configparser
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_cookie() -> str:
    parser = configparser.RawConfigParser()
    parser.read(ROOT / "config.ini", encoding="utf-8-sig")
    for section in parser.sections():
        if parser.has_option(section, "cookie"):
            return parser.get(section, "cookie").strip()
    return ""


def main() -> None:
    cookie = load_cookie()
    url = "https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid=149793525&date=2026-10-03&segment_index=1"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/video/BV1D7411t7Be/",
        "Cookie": cookie,
    })
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
            print(f"status={resp.status} bytes={len(data)} elapsed={time.time()-started:.1f}s")
            print("head:", data[:60])
    except Exception as exc:
        print(f"FAILED after {time.time()-started:.1f}s: {exc!r}")
        code = getattr(exc, "code", None)
        if code:
            print("http code:", code)


main()
