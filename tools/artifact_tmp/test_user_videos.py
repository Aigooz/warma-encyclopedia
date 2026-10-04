import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from tools.bili_api import get_user_videos, get_user_videos_free

for name, fn in [("main_free", lambda: get_user_videos_free(53456, ps=30, max_pages=1)),
                 ("main_wbi", lambda: get_user_videos(53456, ps=30, max_pages=1)),
                 ("small_wbi", lambda: get_user_videos(106320250, ps=30, max_pages=1))]:
    print('\n', name)
    try:
        rows = fn()
        print(len(rows), rows[:3])
    except Exception as exc:
        print('ERROR', exc)
