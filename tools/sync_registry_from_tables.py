from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry.json"
RECONCILED = ROOT / "tools" / "artifact_tmp" / "reconciled_videos.json"

ACCOUNTS = {
    "main_wbi": "主号（Warma）",
    "small_wbi": "小号（warma养鸽场）",
}


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    rows = json.loads(RECONCILED.read_text(encoding="utf-8"))
    by_bvid = {row.get("bvid"): row for row in registry.get("videos", []) if row.get("bvid")}
    added = 0
    updated = 0
    for account_key, label in ACCOUNTS.items():
        for item in rows.get(account_key, []):
            bvid = item.get("bvid")
            if not bvid:
                continue
            canonical = {
                "title": item.get("title", ""),
                "date": item.get("date", ""),
                "type": item.get("type", "其他"),
                "account": label,
                "bvid": bvid,
                "source": item.get("source", "B站用户视频列表"),
            }
            if bvid in by_bvid:
                old = by_bvid[bvid]
                for key, value in canonical.items():
                    if old.get(key) != value:
                        old[key] = value
                        updated += 1
            else:
                new = {
                    "no": None,
                    **canonical,
                    "intro_count": 0,
                    "sub_lines": 0,
                    "sub_chars": 0,
                }
                registry["videos"].append(new)
                by_bvid[bvid] = new
                added += 1

    registry["videos"].sort(key=lambda row: (row.get("date") or "", row.get("bvid") or ""))
    for no, row in enumerate(registry["videos"], 1):
        row["no"] = no

    registry["total_sub_lines"] = sum(row.get("sub_lines") or 0 for row in registry["videos"])
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"added={added} updated_fields={updated} total={len(registry['videos'])}")


if __name__ == "__main__":
    main()
