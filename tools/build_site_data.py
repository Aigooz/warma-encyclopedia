#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 registry.json + B站元数据缓存合并生成 site/data.js。

用法：
  python tools/build_site_data.py           # 生成
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_FILE = ROOT / "registry.json"
CACHE_FILE = ROOT / "tools" / "bili_meta_cache.json"
TAGS_FILE = ROOT / "tools" / "bili_tags_cache.json"
COMMENTS_FILE = ROOT / "tools" / "bili_comments_cache.json"
INSIGHTS_FILE = ROOT / "tools" / "danmaku_insights.json"
ACCOUNT_STATS_FILE = ROOT / "tools" / "account_stats.json"
PROFILES_FILE = ROOT / "tools" / "up_profiles.json"
OUTPUT = ROOT / "site" / "data.js"


def main() -> None:
    registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    tags_cache = {}
    if TAGS_FILE.exists():
        try:
            tags_cache = json.loads(TAGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            tags_cache = {}
    comments_cache = {}
    if COMMENTS_FILE.exists():
        try:
            comments_cache = json.loads(COMMENTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            comments_cache = {}
    insights = {}
    if INSIGHTS_FILE.exists():
        try:
            insights = json.loads(INSIGHTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            insights = {}
    insights_videos = insights.get("videos") or {}
    profiles = {}
    if PROFILES_FILE.exists():
        try:
            profiles = {
                k: v for k, v in json.loads(PROFILES_FILE.read_text(encoding="utf-8")).items()
                if "怒九摸鱼馆" not in k
            }
        except Exception:
            profiles = {}
    followers = {}
    if ACCOUNT_STATS_FILE.exists():
        try:
            snaps = json.loads(ACCOUNT_STATS_FILE.read_text(encoding="utf-8")).get("snapshots") or []
            if snaps:
                followers = snaps[-1].get("accounts") or {}
        except Exception:
            followers = {}

    videos = []
    for row in registry["videos"]:
        bvid = row.get("bvid")
        info = cache.get(bvid) if bvid else None
        if not isinstance(info, dict):
            info = {}
        stat = info.get("stat") or {}
        pubdate = info.get("pubdate")
        pub_dt = None
        if pubdate:
            try:
                pub_dt = datetime.fromtimestamp(int(pubdate), ZoneInfo("Asia/Shanghai"))
            except Exception:
                pub_dt = None
        # 怒九摸鱼馆是联合投稿相关的账号，不作为 Warma 百科的独立账号分类。
        account = row.get("account")
        if account and "怒九摸鱼馆" in account:
            account = "小号（warma养鸽场）"
        # registry 日期优先（因为可能包含精确投稿日），B站 pubdate 作为补充精确到分
        reg_date = row.get("date") or (pub_dt.strftime("%Y-%m-%d") if pub_dt else None)
        videos.append({
            "no": row.get("no"),
            "title": row.get("title"),
            "date": reg_date,
            "pubdate_iso": pub_dt.strftime("%Y-%m-%d %H:%M") if pub_dt else None,
            "type": row.get("type"),
            "account": account,
            "table_source": row.get("source") or "B站用户视频列表",
            "intro_count": row.get("intro_count", 0),
            "sub_lines": row.get("sub_lines"),
            "sub_chars": row.get("sub_chars"),
            "bvid": bvid,
            "aid": info.get("aid"),
            "duration": info.get("duration"),
            "tname": info.get("tname") or None,
            "tags": tags_cache.get(bvid) or [],
            "peaks": (insights_videos.get(bvid) or {}).get("peaks") or [],
            "dm_profile": (insights_videos.get(bvid) or {}).get("profile") or [],
            "memes": (insights_videos.get(bvid) or {}).get("top_phrases") or [],
            "comments": (comments_cache.get(bvid) or {}).get("comments") or [],
            "pic": info.get("pic"),
            "desc": (info.get("desc") or "")[:160],
            "view": stat.get("view"),
            "danmaku": stat.get("danmaku"),
            "reply": stat.get("reply"),
            "favorite": stat.get("favorite"),
            "coin": stat.get("coin"),
            "share": stat.get("share"),
            "like": stat.get("like"),
            "honors": [
                {"type": h.get("type"), "desc": h.get("desc", "")}
                for h in ((info.get("honor_reply") or {}).get("honor") or [])
            ],
        })

    # 按日期升序
    videos.sort(key=lambda v: (v.get("date") or "", v.get("bvid") or ""))
    for i, v in enumerate(videos, 1):
        v["no"] = i

    # 表格联动字段：同账号相邻投稿间隔，以及表格里的数据来源。
    table_last_date = {}
    for v in videos:
        account = v.get("account") or "未分类"
        last_date = table_last_date.get(account)
        if last_date:
            gap_days = max(0, (datetime.strptime(v["date"], "%Y-%m-%d") - datetime.strptime(last_date, "%Y-%m-%d")).days)
            v["gap_days"] = gap_days
            v["gap_band"] = "≤7天" if gap_days <= 7 else "≤30天" if gap_days <= 30 else "≤90天" if gap_days <= 90 else ">90天"
        else:
            v["gap_days"] = None
            v["gap_band"] = None
        table_last_date[account] = v["date"]

    gaps = [v.get("gap_days") for v in videos if isinstance(v.get("gap_days"), int)]
    account_summary = []
    for account in ["主号（Warma）", "小号（warma养鸽场）"]:
        rows = [v for v in videos if v.get("account") == account]
        account_gaps = [v.get("gap_days") for v in rows if isinstance(v.get("gap_days"), int)]
        account_summary.append({
            "account": account,
            "record_count": len(rows),
            "first_date": rows[0].get("date") if rows else None,
            "last_date": rows[-1].get("date") if rows else None,
            "max_gap_days": max(account_gaps) if account_gaps else None,
            "avg_gap_days": round(sum(account_gaps) / len(account_gaps), 1) if account_gaps else None,
        })
    sync_fields = ["title", "bvid", "aid", "date", "type", "duration", "table_source"]
    field_checks = sum(sum(bool(v.get(f)) for f in sync_fields) for v in videos)
    table_sync = {
        "sources": ["@Warma 相关.xlsx", "@warma养鸽场 相关.xlsx"],
        "generated_at": datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M"),
        "record_count": len(videos),
        "field_completeness": round(field_checks / max(1, len(videos) * len(sync_fields)), 4),
        "max_gap_days": max(gaps) if gaps else None,
        "avg_gap_days": round(sum(gaps) / len(gaps), 1) if gaps else None,
        "accounts": account_summary,
    }

    # 全站名梗榜（重复弹幕聚合）
    global_memes = {}
    for ins in insights_videos.values():
        for m in ins.get("top_phrases") or []:
            key = m["content"]
            global_memes[key] = global_memes.get(key, 0) + m["count"]
    top_memes = sorted(global_memes.items(), key=lambda x: -x[1])[:30]

    total_sub_lines = sum(v.get("sub_lines") or 0 for v in videos)
    payload = {
        "docx_version": f"v18-{datetime.now().strftime('%Y%m%d')}",
        "table_sync": table_sync,
        "total_sub_lines": total_sub_lines,
        "total_view": sum(v.get("view") or 0 for v in videos),
        "total_like": sum(v.get("like") or 0 for v in videos),
        "total_danmaku": sum(v.get("danmaku") or 0 for v in videos),
        "total_coin": sum(v.get("coin") or 0 for v in videos),
        "total_reply": sum(v.get("reply") or 0 for v in videos),
        "total_favorite": sum(v.get("favorite") or 0 for v in videos),
        "total_share": sum(v.get("share") or 0 for v in videos),
        "total_duration": sum(v.get("duration") or 0 for v in videos),
        "yearly_danmaku": insights.get("yearly") or {},
        "top_memes": [{"content": k, "count": c} for k, c in top_memes],
        "insights_generated_at": insights.get("generated_at"),
        "comments_fetched": len(comments_cache),
        "followers": followers,
        "profiles": profiles,
        "videos": videos,
    }
    text = "const RAW = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"已生成 {OUTPUT}  视频 {len(videos)} 条  大小 {OUTPUT.stat().st_size/1024:.1f} KB")
    print(f"总播放 {payload['total_view']:,}  总点赞 {payload['total_like']:,}")


if __name__ == "__main__":
    main()
