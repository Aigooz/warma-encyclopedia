import json
import re
from pathlib import Path

base = Path(r'F:\warma百科')
uv = json.loads(Path('user_videos.json').read_text(encoding='utf-8'))
reg = json.loads((base / 'warma-encyclopedia/registry.json').read_text(encoding='utf-8'))['videos']

def norm(x):
    return re.sub(r'\s+', '', str(x or '')).lower()

reg_by_title = {norm(v['title']): v for v in reg}
for k, rows in uv.items():
    print('\n===', k, len(rows), '===')
    print('dates', rows[0]['created'], rows[-1]['created'])
    print('first titles', [r['title'] for r in rows[:5]])
    print('last titles', [r['title'] for r in rows[-5:]])
    matched = [r for r in rows if norm(r['title']) in reg_by_title]
    unmatched = [r for r in rows if norm(r['title']) not in reg_by_title]
    print('registry matched', len(matched), 'unmatched', len(unmatched))
    print('unmatched sample', unmatched[:10])
