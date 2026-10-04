import json
from pathlib import Path

p = Path(r"F:\warma百科\warma-encyclopedia\tools\bili_meta_cache.json")
obj = json.loads(p.read_text(encoding="utf-8"))
print("type", type(obj).__name__, "count", len(obj) if hasattr(obj, "__len__") else None)
if isinstance(obj, dict):
    keys = list(obj.keys())[:5]
    print("keys", keys)
    for k in keys:
        print("\nKEY", k)
        print(json.dumps(obj[k], ensure_ascii=False, indent=2)[:5000])
else:
    print(json.dumps(obj[:2], ensure_ascii=False, indent=2)[:5000])
