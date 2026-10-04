import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from tools.bili_api import get_user_videos, get_user_videos_free

out = {
    'main_free': get_user_videos_free(53456, ps=50, max_pages=20),
    'main_wbi': get_user_videos(53456, ps=50, max_pages=20),
    'small_wbi': get_user_videos(106320250, ps=50, max_pages=20),
}
for k, v in out.items():
    print(k, len(v))
Path('user_videos.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
