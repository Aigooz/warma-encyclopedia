from pathlib import Path
p=Path('tools/build_site_data.py')
s=p.read_text(encoding='utf-8')
s=s.replace('CACHE_FILE = ROOT / "tools" / "bili_meta_cache.json"\nOUTPUT = ROOT / "site" / "data.js"\n', 'CACHE_FILE = ROOT / "tools" / "bili_meta_cache.json"\nTAGS_FILE = ROOT / "tools" / "bili_tags_cache.json"\nOUTPUT = ROOT / "site" / "data.js"\n')
s=s.replace('cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))\n\n    videos = []', 'cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))\n    tags_cache = {}\n    if TAGS_FILE.exists():\n        try:\n            tags_cache = json.loads(TAGS_FILE.read_text(encoding="utf-8"))\n        except Exception:\n            tags_cache = {}\n\n    videos = []')
s=s.replace('            "tname": info.get("tname") or None,\n', '            "tname": info.get("tname") or None,\n            "tags": tags_cache.get(bvid) or [],\n')
p.write_text(s,encoding='utf-8')
print('patched build_site_data')
