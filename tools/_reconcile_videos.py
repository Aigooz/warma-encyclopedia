from __future__ import annotations
import json, re
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path(r"F:\warma百科\warma-encyclopedia")
REG = BASE / "registry.json"
USERS = BASE / "tools/artifact_tmp/user_videos.json"
META = BASE / "tools/bili_meta_cache.json"
OUT = BASE / "tools/artifact_tmp/reconciled_videos.json"

main_videos = json.loads(REG.read_text(encoding="utf-8"))["videos"]
user_lists = json.loads(USERS.read_text(encoding="utf-8"))
meta = json.loads(META.read_text(encoding="utf-8"))


def norm(s: str) -> str:
    return re.sub(r"[\s：:，,。！!？?（）()\[\]【】]+", "", (s or "").lower())


def classify(title: str, desc: str, tid: int | None) -> str:
    text = norm(title) + "\n" + norm(desc)
    radio_words = ["爆米花电台", "爆炸电台", "电台", "radio"]
    live_words = ["直播录像", "直播", "live"]
    game_words = [
        "游戏实况", "游戏介绍", "游戏试玩", "游戏攻略", "游戏相关", "游戏", "实况", "试玩",
        "独立游戏", "电子竞技", "单机游戏", "switch", "steam", "ns", "3ds", "splatoon",
        "星之卡比", "旷野之息", "塞尔达", "动物森友会", "动物森", "岛上", "overcooked",
        "celeste", "ori", "undertale", "dead cells", "cooking simulator",
        "untitled goose game", "gonner", "a dark room", "party", "派对", "音游", "音乐游戏",
        "米老鼠", "迪士尼", "律师函", "qwop", "fc", "nes"
    ]
    music_words = ["翻唱", "合唱", "唱歌", "演唱", "音乐", "原创", "演奏", "vocaloid", "utau", "mv", "acg"]
    paint_words = ["绘画", "画画", "手绘", "手书", "动画", "mad", "amv", "mmd"]
    dub_words = ["配音", "中文配音", "小剧场", "短片", "小短剧", "短剧"]
    funny_words = ["搞笑", "沙雕", "娱乐", "鬼畜", "爆笑", "有趣", "整活"]
    know_words = ["学习", "科普", "科学", "高考", "中考", "励志", "教育", "知识"]
    life_words = ["日常", "生活", "vlog", "种田", "做饭", "旅行", "老家", "美食", "料理"]
    if any(w in text for w in radio_words): return "爆炸电台"
    if any(w in text for w in live_words): return "直播录像"
    if any(w in text for w in game_words): return "游戏实况"
    if any(w in text for w in music_words): return "翻唱/音乐"
    if any(w in text for w in know_words): return "知识科普"
    if any(w in text for w in paint_words) and any(w in text for w in dub_words): return "配音/小剧场"
    if any(w in text for w in paint_words): return "绘画/手书"
    if any(w in text for w in dub_words): return "配音/小剧场"
    if any(w in text for w in funny_words): return "搞笑娱乐"
    if any(w in text for w in life_words): return "生活日常"
    if tid in {17, 172, 65, 230, 126}: return "游戏实况"
    if tid in {31, 28, 30, 59}: return "翻唱/音乐"
    if tid in {47, 162, 161, 136}: return "绘画/手书"
    if tid in {21, 76, 222, 228, 229, 250, 257, 251}: return "生活日常"
    if tid == 138: return "搞笑娱乐"
    if tid == 174: return "直播录像"
    if tid == 27: return "影视/综艺"
    return "其他"


registry_by_bvid = {r.get("bvid"): r for r in main_videos if r.get("bvid")}
registry_by_title = {norm(r.get("title", "")): r for r in main_videos if r.get("title")}

result = {}
for account_key, account_label in [("main_wbi", "Warma"), ("small_wbi", "warma养鸽场")]:
    rows = []
    for item in user_lists.get(account_key, []):
        bvid = item.get("bvid")
        m = meta.get(bvid) or {}
        reg = registry_by_bvid.get(bvid) or registry_by_title.get(norm(item.get("title", ""))) or {}
        title = item.get("title") or reg.get("title") or ""
        created = item.get("created") or m.get("pubdate") or m.get("ctime")
        dt = datetime.fromtimestamp(created, timezone(timedelta(hours=8))) if created else None
        date = dt.date().isoformat() if dt else ""
        duration = m.get("duration") or 0
        aid = item.get("aid") or m.get("aid") or ""
        tid = m.get("tid")
        ctype = reg.get("type") or classify(title, m.get("desc", ""), tid)
        rows.append({
            "title": title,
            "bvid": bvid,
            "aid": aid,
            "date": date,
            "type": ctype,
            "duration": duration,
            "link": f"https://www.bilibili.com/video/{bvid}",
            "source": "B站用户视频 + B站元数据",
            "matched_registry": bool(reg),
        })
    rows.sort(key=lambda x: (x["date"], x["title"]))
    result[account_key] = rows
    print(account_key, account_label, "count", len(rows), "matched_registry", sum(r["matched_registry"] for r in rows), "no_date", sum(not r["date"] for r in rows), "no_bvid", sum(not r["bvid"] for r in rows), "no_aid", sum(not r["aid"] for r in rows), "no_duration", sum(not r["duration"] for r in rows), "other", sum(r["type"] == "其他" for r in rows))
    print("first3", rows[:3])
    print("last3", rows[-3:])

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved", OUT)
