import json
import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from tools.update_warma_xlsx import fetch_bili_meta

base = Path(r'F:\warma百科')
uv = json.loads(Path('user_videos.json').read_text(encoding='utf-8'))
cache_path = base / 'warma-encyclopedia/tools/bili_meta_cache.json'
cache = json.loads(cache_path.read_text(encoding='utf-8'))
todo = []
for rows in uv.values():
    for r in rows:
        bv = r['bvid']
        if bv not in cache:
            todo.append(bv)
todo = list(dict.fromkeys(todo))
print('todo', len(todo))
for i, bv in enumerate(todo, 1):
    cache[bv] = fetch_bili_meta(bv)
    if i % 10 == 0 or i == len(todo):
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    print(i, bv, cache[bv].get('title'), cache[bv].get('_error'))
    time.sleep(0.14)
