# -*- coding: utf-8 -*-
"""
gen_charts2.py — 深度可视化：话题关键词 / 内容演变 / 类型×字幕量交叉分析
"""
import json, os, re
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = r'F:\warma百科\warma-encyclopedia'
CHARTS = os.path.join(ROOT, 'charts')

# 颜色
PINK='#E8919C'; LAV='#B39DDB'; BLUE='#82B1FF'; MINT='#80CBC4'; AMBER='#FFD54F'
CORAL='#FF8A65'; PURPLE='#CE93D8'; TEAL='#4DB6AC'; ROSE='#F48FB1'; SKY='#81D4FA'
GRID='#E0E0E0'; TEXT='#37474F'
COLORS = [PINK, LAV, BLUE, MINT, AMBER, CORAL, PURPLE, TEAL, ROSE, SKY]

plt.rcParams.update({
    'font.family': ['Microsoft YaHei','SimHei','sans-serif'],
    'font.size': 11, 'axes.unicode_minus': False,
    'figure.facecolor': 'white', 'axes.facecolor': 'white',
    'axes.edgecolor': GRID, 'axes.labelcolor': TEXT,
    'xtick.color': TEXT, 'ytick.color': TEXT, 'text.color': TEXT,
})

def style_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(GRID)
    ax.spines['bottom'].set_color(GRID)
    ax.grid(axis='y', color=GRID, linewidth=0.5, alpha=0.6)
    ax.set_axisbelow(True)

# 从 docx 提取字幕文本
from docx import Document
doc = Document(os.path.join(ROOT, 'warma-encyclopedia-v15.docx'))
paras = doc.paragraphs

# 收集所有字幕文本
all_sub_text = []
in_sub = False
for p in paras:
    t = p.text.strip()
    if t.startswith('字幕全文'):
        in_sub = True; continue
    if in_sub and (t.startswith('— 第') and '完' in t):
        in_sub = False; continue
    if in_sub and t and not t.startswith('（共'):
        all_sub_text.append(t)

full_text = ' '.join(all_sub_text)
print(f'提取字幕总字数: {len(full_text)}')

# ========== 9. 话题关键词 TOP30 ==========
TOPIC_MAP = {
    '音乐': ['歌','唱','曲','音乐','旋律','副歌','编曲','伴奏','翻唱','原创','录音','高音','音准','节奏','调'],
    '游戏': ['游戏','实况','关卡','boss','血量','存档','地图','角色','装备','道具','操作','手残','通关','steam','switch','塞尔达','马力欧','splatoon'],
    '美食': ['吃','好吃','美食','饿','饭','菜','肉','火锅','烧烤','零食','甜','辣','味道','汉堡','拉面','奶茶'],
    '日常生活': ['今天','昨天','明天','学校','上课','作业','考试','家','妈','爸','妹妹','姐姐','睡觉','起床','洗澡','出门','快递'],
    '童年/回忆': ['小时候','初中','高中','以前','当年','童年','回忆','那时候','曾经','小学'],
    '社交/合作': ['朋友','一起','我们','大家','合作','队友','同学','聊天'],
    '情感': ['喜欢','爱','开心','难过','感动','哭','笑','伤心','生气','委屈','孤独'],
    '绘画/创作': ['画','画了','手书','投稿','制作','素材','剪辑','视频','动画','渲染','软件'],
    '学习/知识': ['学习','知识','生物','数学','英语','语文','教材','课本','考试','复习'],
    '直播互动': ['直播','弹幕','观众','礼物','舰长','连麦','提问','评论'],
}
CATCH = [
    ('诶', r'诶'), ('哇', r'哇'), ('啊啊啊', r'啊啊啊+'), ('哈哈哈', r'哈{3,}'),
    ('拜拜', r'拜拜'), ('我的天', r'我的天'), ('好耶', r'好耶'), ('离谱', r'离谱'),
    ('救命', r'救命'), ('完了', r'完了'), ('怎么办', r'怎么办'), ('芜湖', r'芜?湖'),
    ('炸了', r'炸了'), ('优雅', r'优雅'), ('嘿嘿', r'嘿{2,}'),
]

# 话题频次
topic_scores = {}
low = full_text.lower()
for cat, kws in TOPIC_MAP.items():
    c = sum(low.count(k) for k in kws)
    if c > 0:
        topic_scores[cat] = c

top_topics = sorted(topic_scores.items(), key=lambda x: -x[1])[:10]
labels_t = [t[0] for t in top_topics]
values_t = [t[1] for t in top_topics]

fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
y_pos = range(len(labels_t))
bars = ax.barh(y_pos, values_t, color=[COLORS[i % len(COLORS)] for i in range(len(labels_t))], height=0.6, edgecolor='white', linewidth=0.5, zorder=3)
ax.set_yticks(y_pos); ax.set_yticklabels(labels_t, fontsize=10)
ax.invert_yaxis()
for bar, val in zip(bars, values_t):
    ax.text(bar.get_width() + max(values_t)*0.01, bar.get_y() + bar.get_height()/2, f'{val}',
            va='center', fontsize=10, color=TEXT, fontweight='bold')
ax.set_xlabel('关键词出现次数', fontsize=12)
ax.set_title('话题关键词频次 TOP10', fontsize=14, fontweight='bold', pad=12)
style_ax(ax)
ax.grid(axis='x', color=GRID, linewidth=0.5, alpha=0.6)
ax.grid(axis='y', visible=False)
ax.set_xlim(0, max(values_t) * 1.12)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, '09_topics.png'), bbox_inches='tight', facecolor='white')
plt.close(fig)
print('✓ 09_topics.png')

# ========== 10. 口头禅/语气词频率 ==========
# 与第1.5节“标志性口头禅使用频率TOP20”保持同一统计口径。
CATCH_TABLE_TOP15 = [
    ('诶', 2720), ('哇', 1756), ('哈哈', 767), ('嘿嘿', 454),
    ('天哪', 331), ('拜拜', 281), ('啊啊啊', 212), ('诶诶', 199),
    ('没问题', 181), ('我的天', 94), ('好的好的', 89), ('救命', 45),
    ('吓死', 41), ('炸了', 32), ('我真棒', 25),
]
catch_data = CATCH_TABLE_TOP15
labels_c = [c[0] for c in catch_data]
values_c = [c[1] for c in catch_data]

fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
bars = ax.barh(range(len(labels_c)), values_c, color=PINK, height=0.55, edgecolor='white', linewidth=0.5, zorder=3)
ax.set_yticks(range(len(labels_c))); ax.set_yticklabels(labels_c, fontsize=11)
ax.invert_yaxis()
for bar, val in zip(bars, values_c):
    ax.text(bar.get_width() + max(values_c)*0.01, bar.get_y() + bar.get_height()/2, f'{val:,}',
            va='center', fontsize=10, color=TEXT, fontweight='bold')
ax.set_xlabel('出现次数', fontsize=12)
ax.set_title('口头禅/语气词使用频率 TOP15', fontsize=14, fontweight='bold', pad=12)
style_ax(ax)
ax.grid(axis='x', color=GRID, linewidth=0.5, alpha=0.6)
ax.grid(axis='y', visible=False)
ax.set_xlim(0, max(values_c) * 1.12)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, '10_catchphrases.png'), bbox_inches='tight', facecolor='white')
plt.close(fig)
print('✓ 10_catchphrases.png')

# ========== 11. 内容类型年度演变（堆叠面积图）==========
# 读取 registry
with open(os.path.join(ROOT, 'registry.json'), 'r', encoding='utf-8') as f:
    reg = json.load(f)
vids = reg['videos']

# 简化类型
def simplify(t):
    if '游戏' in t or '实况' in t: return '游戏实况'
    if '翻唱' in t or '音乐' in t or '原创' in t: return '音乐/翻唱'
    if '电台' in t: return '爆炸电台'
    if '直播' in t: return '直播录像'
    if '生活' in t or '日常' in t or '杂谈' in t or 'Vlog' in t: return '生活/杂谈'
    return '其他'

year_type = defaultdict(lambda: defaultdict(int))
for v in vids:
    y = v['date'][:4]
    st = simplify(v.get('type', ''))
    year_type[y][st] += 1

years_sorted = sorted(year_type.keys())
type_names = ['游戏实况', '音乐/翻唱', '直播录像', '爆炸电台', '生活/杂谈', '其他']
type_colors = [BLUE, PINK, AMBER, LAV, MINT, '#CFD8DC']

# 每年各类型占比
data_matrix = []
for y in years_sorted:
    total = sum(year_type[y].values())
    row = [year_type[y].get(t, 0) / total * 100 for t in type_names]
    data_matrix.append(row)
data_matrix = np.array(data_matrix).T  # shape: (n_types, n_years)

fig, ax = plt.subplots(figsize=(11, 5.5), dpi=200)
ax.stackplot(range(len(years_sorted)), data_matrix, labels=type_names, colors=type_colors, alpha=0.85)
ax.set_xticks(range(len(years_sorted)))
ax.set_xticklabels(years_sorted, fontsize=10)
ax.set_ylabel('占比（%）', fontsize=12)
ax.set_ylim(0, 100)
ax.set_title('内容类型年度演变', fontsize=14, fontweight='bold', pad=12)
ax.legend(loc='upper left', fontsize=9, frameon=False, ncol=2)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(GRID); ax.spines['bottom'].set_color(GRID)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, '11_type_evolution.png'), bbox_inches='tight', facecolor='white')
plt.close(fig)
print('✓ 11_type_evolution.png')

# ========== 12. 类型×平均字幕量（气泡图）==========
type_stats = defaultdict(lambda: {'count': 0, 'chars': 0, 'lines': 0})
for v in vids:
    st = simplify(v.get('type', ''))
    type_stats[st]['count'] += 1
    type_stats[st]['chars'] += v.get('sub_chars', 0)
    type_stats[st]['lines'] += v.get('sub_lines', 0)

t_labels = list(type_stats.keys())
t_counts = [type_stats[t]['count'] for t in t_labels]
t_avg_chars = [type_stats[t]['chars'] / max(1, type_stats[t]['count']) / 1000 for t in t_labels]  # 千字符
t_total_chars = [type_stats[t]['chars'] / 10000 for t in t_labels]  # 万字符

fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
scatter = ax.scatter(t_counts, t_avg_chars, s=[max(50, c*30) for c in t_total_chars],
                     c=[COLORS[i % len(COLORS)] for i in range(len(t_labels))],
                     alpha=0.7, edgecolors='white', linewidth=1.5, zorder=3)
for i, t in enumerate(t_labels):
    ax.annotate(f'{t}\n({t_counts[i]}部, 均{t_avg_chars[i]:.1f}k字)',
                (t_counts[i], t_avg_chars[i]),
                textcoords="offset points", xytext=(0, 14),
                ha='center', fontsize=8.5, color=TEXT)
ax.set_xlabel('视频数量（部）', fontsize=12)
ax.set_ylabel('平均字幕量（千字符/部）', fontsize=12)
ax.set_title('视频类型 × 平均字幕量（气泡大小=总字幕量）', fontsize=14, fontweight='bold', pad=12)
style_ax(ax)
ax.grid(color=GRID, linewidth=0.5, alpha=0.5)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, '12_type_scatter.png'), bbox_inches='tight', facecolor='white')
plt.close(fig)
print('✓ 12_type_scatter.png')

print('\n✅ 深度可视化完成（09-12）')
