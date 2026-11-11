# -*- coding: utf-8 -*-
"""把微博缓存整理成站点/App 可用的 weibo 数据块。

输入：tools/weibo_warma_cache.json / tools/weibo_nujiu_cache.json
输出：site/data-weibo.js（同时被 data.js 的构建脚本引用）

微博文本来自 m.weibo.cn 公开接口，含 HTML 表情标记。这里会：
  - 去掉 HTML 标签，把表情 img 还原成 [表情名]；
  - 解析 created_at 为 ISO 日期；
  - 保留互动数与配图，供客户端展示。
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCES = {
    "warma": ROOT / "tools" / "weibo_warma_cache.json",
    "nujiu": ROOT / "tools" / "weibo_nujiu_cache.json",
}
OUT = ROOT / "site" / "data-weibo.js"

IMAGE_TAG = re.compile(r'<img[^>]*alt="([^"]*)"[^>]*>', re.I)
TAG = re.compile(r"<[^>]+>")
LINK = re.compile(r'<a[^>]*>(.*?)</a>', re.I | re.S)


def clean_text(raw: str) -> str:
    if not raw:
        return ""
    # 表情的 alt 通常已经自带方括号（如 [馋嘴]），只有缺括号时才补。
    def emoji(match):
        name = match.group(1).strip()
        return name if name.startswith("[") else "[%s]" % name

    text = IMAGE_TAG.sub(emoji, raw)
    text = LINK.sub(lambda m: m.group(1), text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = TAG.sub("", text)
    text = html.unescape(text)
    text = text.replace("\u200b", "")
    text = text.replace("...全文", "").replace("收起", "")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def parse_created(value: str) -> str:
    """微博返回形如 `Tue Nov 10 21:39:48 +0800 2026`。"""
    try:
        return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d %H:%M")
    except Exception:
        return value or ""


def main() -> None:
    payload = {}
    for key, path in SOURCES.items():
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        posts = []
        for item in data.get("posts") or []:
            text = clean_text(item.get("text", ""))
            if not text:
                continue
            posts.append({
                "id": str(item.get("id") or ""),
                "date": parse_created(item.get("created_at", "")),
                "text": text,
                "reposts": item.get("reposts") or 0,
                "comments": item.get("comments") or 0,
                "likes": item.get("attitudes") or 0,
                "region": item.get("region") or "",
                "pics": item.get("pics") or [],
                "url": "https://m.weibo.cn/status/%s" % item.get("bid", ""),
            })
        posts.sort(key=lambda p: p["date"], reverse=True)
        payload[key] = {
            "uid": data.get("uid"),
            "fetched_at": data.get("fetched_at"),
            "count": len(posts),
            "posts": posts,
        }
    OUT.write_text("const WEIBO = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
                   encoding="utf-8")
    for key, value in payload.items():
        print("%s: %d 条微博 -> %s" % (key, value["count"], OUT.name))


if __name__ == "__main__":
    main()
