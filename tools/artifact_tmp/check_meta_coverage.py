import json
from pathlib import Path

base = Path(r'F:\warma百科')
uv = json.loads(Path('user_videos.json').read_text(encoding='utf-8'))
meta = json.loads((base / 'warma-encyclopedia/tools/bili_meta_cache.json').read_text(encoding='utf-8'))

for k, rows in uv.items():
    missing = [r for r in rows if r['bvid'] not in meta]
    bad = [r for r in rows if r['bvid'] in meta and isinstance(meta[r['bvid']], dict) and '_error' in meta[r['bvid']]]
    print('\n', k, 'rows', len(rows), 'missing meta', len(missing), 'bad meta', len(bad))
    print('missing sample', missing[:10])
    print('bad sample', bad[:10])
