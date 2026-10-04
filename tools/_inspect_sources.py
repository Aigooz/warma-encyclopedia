import json
from pathlib import Path

base = Path(r"F:\warma百科\warma-encyclopedia")

for name in ["registry.json", "tools/artifact_tmp/user_videos.json", "tools/up_profiles.json", "tools/account_stats.json"]:
    p = base / name
    print("\n###", name, p.stat().st_size)
    obj = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(obj, list):
        print("type list count", len(obj))
        print(json.dumps(obj[:2], ensure_ascii=False, indent=2)[:4000])
    elif isinstance(obj, dict):
        print("type dict keys", list(obj.keys())[:30])
        for k in list(obj.keys())[:3]:
            print(k, json.dumps(obj[k], ensure_ascii=False, indent=2)[:3000])
