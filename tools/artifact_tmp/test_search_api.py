import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from tools.bili_api import _get

for title in ["【自制阿松手书】我的哥，威力永恒 (慎入）", "【warma】版权警告！！"]:
    data = _get('https://api.bilibili.com/x/web-interface/search/type', {
        'search_type': 'video',
        'keyword': title,
    })
    print('\n', title, 'code', data.get('code'), 'message', data.get('message'))
    results = data.get('data', {}).get('result') or []
    for r in results[:5]:
        print(r.get('bvid'), r.get('aid'), r.get('title'), r.get('author'), r.get('mid'))
