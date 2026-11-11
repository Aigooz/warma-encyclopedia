# -*- coding: utf-8 -*-
"""重抓全部空字幕（复用修正后的 player/v2 回退逻辑）。

用法：python tools/refill_subtitles_all.py [--repo nujiu]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPOS = {
    "warma": Path(r"F:\沃怒百科\warma百科\warma-encyclopedia"),
    "nujiu": Path(r"F:\沃怒百科\怒九百科\怒九百科"),
}


def refill(root: Path, rounds: int = 3) -> None:
    sys.path.insert(0, str(root / "tools"))
    import importlib
    import bili_api
    importlib.reload(bili_api)
    sub_dir = root / "subtitles"
    registry = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    videos = registry.get("videos") or []
    targets = []
    for row in videos:
        bvid = row.get("bvid")
        if not bvid:
            continue
        path = sub_dir / f"{bvid}.json"
        lines = []
        if path.exists():
            try:
                lines = json.loads(path.read_text(encoding="utf-8")).get("lines") or []
            except Exception:
                lines = []
        if not lines:
            targets.append((row, path))
    print(f"[{root.name}] 空字幕 {len(targets)} 条，开始回填", flush=True)
    filled = 0
    for round_index in range(rounds):
        remaining = []
        for row, path in targets:
            bvid = row["bvid"]
            try:
                info = bili_api.get_video_info(bvid)
                lines = []
                for page in info.get("pages") or [{"cid": info.get("cid")}]:
                    cid = page.get("cid")
                    if cid:
                        lines.extend(bili_api.get_subtitle_lines(bvid, cid))
                        time.sleep(0.05)
                if lines:
                    payload = {"bvid": bvid, "title": info["title"],
                               "desc": info.get("desc", ""), "pubdate": info["pubdate"],
                               "owner_mid": (info.get("owner") or {}).get("mid"),
                               "owner_name": (info.get("owner") or {}).get("name"),
                               "lines": lines}
                    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                                    encoding="utf-8")
                    row["sub_lines"] = len(lines)
                    row["sub_chars"] = sum(len(x) for x in lines)
                    filled += 1
                    print(f"  + {bvid} {len(lines)} 行", flush=True)
                else:
                    remaining.append((row, path))
                time.sleep(0.12)
            except Exception as exc:
                print(f"  ! {bvid} {type(exc).__name__}: {str(exc)[:80]}", flush=True)
                remaining.append((row, path))
        targets = remaining
        print(f"[{root.name}] 第 {round_index + 1} 轮结束，仍缺 {len(targets)}", flush=True)
        if not targets:
            break
    if filled:
        registry["total_sub_lines"] = sum(r.get("sub_lines") or 0 for r in videos)
        (root / "registry.json").write_text(
            json.dumps(registry, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[{root.name}] 补回 {filled} 条字幕，台账已更新", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", choices=list(REPOS), default=None)
    parser.add_argument("--rounds", type=int, default=3)
    args = parser.parse_args()
    names = [args.repo] if args.repo else list(REPOS)
    for name in names:
        refill(REPOS[name], args.rounds)


if __name__ == "__main__":
    main()
