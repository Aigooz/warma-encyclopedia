from pathlib import Path
p=Path('tools/classify_videos.py')
s=p.read_text(encoding='utf-8')
s=s.replace("    if hit(full,PAINT_WORDS) and hit(full,DUB_WORDS): return '配音/小剧场'\n    if hit(full,PAINT_WORDS): return '绘画/手书'\n    if hit(full,DUB_WORDS): return '配音/小剧场'\n    if hit(full,KNOW_WORDS): return '知识科普'\n    if hit(full,GAME_WORDS): return '游戏实况'\n    if hit(full,MUSIC_WORDS): return '翻唱/音乐'\n    if hit(full,FUNNY_WORDS): return '搞笑娱乐'\n    if hit(full,LIFE_WORDS): return '生活日常'\n", "    if hit(full,GAME_WORDS): return '游戏实况'\n    if hit(full,MUSIC_WORDS): return '翻唱/音乐'\n    if hit(full,KNOW_WORDS): return '知识科普'\n    if hit(full,PAINT_WORDS) and hit(full,DUB_WORDS): return '配音/小剧场'\n    if hit(full,PAINT_WORDS): return '绘画/手书'\n    if hit(full,DUB_WORDS): return '配音/小剧场'\n    if hit(full,FUNNY_WORDS): return '搞笑娱乐'\n    if hit(full,LIFE_WORDS): return '生活日常'\n")
p.write_text(s,encoding='utf-8')
print('patched')
