# -*- coding: utf-8 -*-
"""
gen_charts.py — 为 warma 百科生成可视化图表（PNG）
输出到 charts/ 目录，供 docx 嵌入和 HTML 仪表板使用。
"""
import json, os, re
from collections import Counter, defaultdict
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

ROOT = r'F:\warma百科\warma-encyclopedia'
CHARTS = os.path.join(ROOT, 'charts')
os.makedirs(CHARTS, exist_ok=True)

# ---------- 加载数据 ----------
with open(os.path.join(ROOT, 'registry.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)
vids = data['videos']

# ---------- 配色 ----------
PALETTE = {
    'pink':    '#E8919C',
    'lavender':'#B39DDB',
    'blue':    '#82B1FF',
    'mint':    '#80CBC4',
    'amber':   '#FFD54F',
    'coral':   '#FF8A65',
    'purple':  '#CE93D8',
    'teal':    '#4DB6AC',
    'rose':    '#F48FB1',
    'sky':     '#81D4FA',
    'grey':    '#CFD8DC',
    'bg':      '#FFFFFF',
    'text':    '#37474F',
    'grid':    '#E0E0E0',
}
COLORS = list(PALETTE[k] for k in ['pink','lavender','blue','mint','amber','coral','purple','teal','rose','sky'])

plt.rcParams.update({
    'font.family': ['Microsoft YaHei', 'SimHei', 'sans-serif'],
    'font.size': 11,
    'axes.unicode_minus': False,
    'figure.facecolor': PALETTE['bg'],
    'axes.facecolor': PALETTE['bg'],
    'axes.edgecolor': PALETTE['grid'],
    'axes.labelcolor': PALETTE['text'],
    'xtick.color': PALETTE['text'],
    'ytick.color': PALETTE['text'],
    'text.color': PALETTE['text'],
})

def style_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(PALETTE['grid'])
    ax.spines['bottom'].set_color(PALETTE['grid'])
    ax.grid(axis='y', color=PALETTE['grid'], linewidth=0.5, alpha=0.6)
    ax.set_axisbelow(True)

# ========== 1. 年度投稿趋势 ==========
years_counter = Counter(v['date'][:4] for v in vids if v.get('date'))
year_labels = sorted(years_counter)
year_vals = [years_counter[y] for y in year_labels]

fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
bars = ax.bar(year_labels, year_vals, color=PALETTE['pink'], width=0.65, edgecolor='white', linewidth=0.8, zorder=3)
for bar, val in zip(bars, year_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, str(val),
            ha='center', va='bottom', fontsize=11, fontweight='bold', color=PALETTE['text'])
ax.set_xlabel('年份', fontsize=12)
ax.set_ylabel('投稿数量', fontsize=12)
ax.set_title('Warma 年度投稿趋势（2015–2026）', fontsize=14, fontweight='bold', pad=12)
style_ax(ax)
ax.set_ylim(0, max(year_vals) * 1.15)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, '01_yearly_trend.png'), bbox_inches='tight', facecolor='white')
plt.close(fig)
print('✓ 01_yearly_trend.png')

# ========== 2. 内容类型分布（环形图）==========
type_counter = Counter(v['type'] for v in vids)
# 合并小类
main_types = [(t, c) for t, c in type_counter.most_common() if c >= 5]
other_count = sum(c for t, c in type_counter.most_common() if c < 5)
if other_count > 0:
    main_types.append(('其他', other_count))
labels = [t for t, _ in main_types]
sizes = [c for _, c in main_types]

fig, ax = plt.subplots(figsize=(9, 7), dpi=200)
wedges, texts, autotexts = ax.pie(
    sizes, labels=None, autopct=lambda p: f'{p:.1f}%\n({int(round(p*sum(sizes)/100))}部)',
    startangle=90, pctdistance=0.78,
    colors=COLORS[:len(sizes)],
    wedgeprops=dict(width=0.42, edgecolor='white', linewidth=2)
)
for at in autotexts:
    at.set_fontsize(9)
    at.set_fontweight('bold')
    at.set_color('white')
# 中心文字
ax.text(0, 0.06, f'{sum(sizes)}', ha='center', va='center', fontsize=28, fontweight='bold', color=PALETTE['text'])
ax.text(0, -0.14, '部视频', ha='center', va='center', fontsize=13, color=PALETTE['text'])
# 图例
ax.legend(wedges, [f'{t} ({c})' for t, c in zip(labels, sizes)],
          loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=10, frameon=False)
ax.set_title('Warma 视频类型分布', fontsize=14, fontweight='bold', pad=12)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, '02_type_donut.png'), bbox_inches='tight', facecolor='white')
plt.close(fig)
print('✓ 02_type_donut.png')

# ========== 3. 月度投稿热力图（简化为年×月矩阵）==========
month_matrix = np.zeros((12, len(year_labels)))  # rows=months, cols=years
for v in vids:
    d = v.get('date', '')
    if len(d) >= 7:
        y = d[:4]
        m = int(d[5:7]) - 1
        if y in year_labels:
            month_matrix[m, year_labels.index(y)] += 1

fig, ax = plt.subplots(figsize=(12, 5.5), dpi=200)
im = ax.imshow(month_matrix, aspect='auto', cmap='RdPu', vmin=0)
ax.set_xticks(range(len(year_labels)))
ax.set_xticklabels(year_labels, fontsize=10)
ax.set_yticks(range(12))
ax.set_yticklabels(['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'], fontsize=9)
# 在每个格子上显示数字
for i in range(12):
    for j in range(len(year_labels)):
        val = int(month_matrix[i, j])
        if val > 0:
            color = 'white' if val > month_matrix.max() * 0.5 else PALETTE['text']
            ax.text(j, i, str(val), ha='center', va='center', fontsize=8, color=color, fontweight='bold')
ax.set_title('月度投稿热力图', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('年份', fontsize=12)
cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label('投稿数量', fontsize=10)
ax.spines[:].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, '03_monthly_heatmap.png'), bbox_inches='tight', facecolor='white')
plt.close(fig)
print('✓ 03_monthly_heatmap.png')

# ========== 4. 字幕量趋势（累计曲线）==========
sorted_vids = sorted([v for v in vids if v.get('date')], key=lambda x: x['date'])
dates = [datetime.strptime(v['date'], '%Y-%m-%d') for v in sorted_vids]
cum_chars = np.cumsum([v.get('sub_chars', 0) for v in sorted_vids])
cum_lines = np.cumsum([v.get('sub_lines', 0) for v in sorted_vids])

fig, ax1 = plt.subplots(figsize=(11, 5), dpi=200)
ax1.fill_between(dates, cum_chars / 10000, alpha=0.3, color=PALETTE['pink'], zorder=2)
ax1.plot(dates, cum_chars / 10000, color=PALETTE['pink'], linewidth=2, zorder=3, label='累计字幕字数')
ax1.set_ylabel('累计字幕字数（万）', fontsize=12, color=PALETTE['pink'])
ax1.tick_params(axis='y', labelcolor=PALETTE['pink'])
ax2 = ax1.twinx()
ax2.plot(dates, cum_lines / 1000, color=PALETTE['lavender'], linewidth=2, zorder=3, label='累计字幕行数')
ax2.set_ylabel('累计字幕行数（千）', fontsize=12, color=PALETTE['lavender'])
ax2.tick_params(axis='y', labelcolor=PALETTE['lavender'])
ax2.spines['top'].set_visible(False)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax1.xaxis.set_major_locator(mdates.YearLocator())
style_ax(ax1)
ax1.set_title('字幕累计增长趋势', fontsize=14, fontweight='bold', pad=12)
# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10, frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, '04_subtitle_growth.png'), bbox_inches='tight', facecolor='white')
plt.close(fig)
print('✓ 04_subtitle_growth.png')

# ========== 5. 主号/小号投稿分布 ==========
acct_counter = Counter(v.get('account', '未知') for v in vids)
acct_labels = list(acct_counter.keys())
acct_sizes = list(acct_counter.values())
acct_colors = [PALETTE['pink'], PALETTE['blue'], PALETTE['mint']][:len(acct_labels)]

fig, ax = plt.subplots(figsize=(8, 5), dpi=200)
bars = ax.barh(acct_labels, acct_sizes, color=acct_colors, height=0.5, edgecolor='white', linewidth=0.8, zorder=3)
for bar, val in zip(bars, acct_sizes):
    ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, f'{val} ({val/sum(acct_sizes)*100:.1f}%)',
            va='center', fontsize=11, fontweight='bold', color=PALETTE['text'])
ax.set_xlabel('投稿数量', fontsize=12)
ax.set_title('主号与 小号投稿分布', fontsize=14, fontweight='bold', pad=12)
style_ax(ax)
ax.grid(axis='x', color=PALETTE['grid'], linewidth=0.5, alpha=0.6)
ax.grid(axis='y', visible=False)
ax.set_xlim(0, max(acct_sizes) * 1.25)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, '05_account_dist.png'), bbox_inches='tight', facecolor='white')
plt.close(fig)
print('✓ 05_account_dist.png')

# ========== 6. 投稿间隔分析 ==========
gaps = []
for i in range(1, len(dates)):
    gap = (dates[i] - dates[i-1]).days
    if gap > 0:
        gaps.append((dates[i], gap))

fig, ax = plt.subplots(figsize=(11, 4.5), dpi=200)
ax.scatter([g[0] for g in gaps], [g[1] for g in gaps], s=8, c=PALETTE['pink'], alpha=0.35, edgecolors='none', zorder=3)
# 7日均线
ax.axhline(y=7, color=PALETTE['lavender'], linestyle='--', linewidth=1.5, alpha=0.7, label='7天参考线')
ax.axhline(y=30, color=PALETTE['amber'], linestyle='--', linewidth=1.5, alpha=0.7, label='30天参考线')
ax.set_ylabel('距上次投稿（天）', fontsize=12)
ax.set_title('投稿间隔分布', fontsize=14, fontweight='bold', pad=12)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator())
style_ax(ax)
ax.legend(fontsize=10, frameon=False)
ax.set_ylim(0, min(max(g[1] for g in gaps), 200))
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, '06_upload_gaps.png'), bbox_inches='tight', facecolor='white')
plt.close(fig)
print('✓ 06_upload_gaps.png')

# ========== 7. 单视频字幕量 TOP20 ==========
top_vids = sorted(vids, key=lambda x: x.get('sub_chars', 0), reverse=True)[:20]
top_labels = [f"#{v['no']} {v['title'][:12]}..." if len(v['title']) > 12 else f"#{v['no']} {v['title']}" for v in top_vids]
top_vals = [v.get('sub_chars', 0) / 1000 for v in top_vids]

fig, ax = plt.subplots(figsize=(10, 8), dpi=200)
y_pos = range(len(top_vids))
bars = ax.barh(y_pos, top_vals, color=PALETTE['lavender'], height=0.6, edgecolor='white', linewidth=0.5, zorder=3)
ax.set_yticks(y_pos)
ax.set_yticklabels(top_labels, fontsize=8.5)
ax.invert_yaxis()
for bar, val in zip(bars, top_vals):
    ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2, f'{val:.1f}k',
            va='center', fontsize=9, color=PALETTE['text'])
ax.set_xlabel('字幕字数（千字符）', fontsize=12)
ax.set_title('字幕量最多的 20 部视频', fontsize=14, fontweight='bold', pad=12)
style_ax(ax)
ax.grid(axis='x', color=PALETTE['grid'], linewidth=0.5, alpha=0.6)
ax.grid(axis='y', visible=False)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, '07_top_subtitle.png'), bbox_inches='tight', facecolor='white')
plt.close(fig)
print('✓ 07_top_subtitle.png')

# ========== 8. 自我介绍频率 ==========
intro_vids = [(v['date'], v.get('intro_count', 0)) for v in sorted_vids]
intro_dates = [datetime.strptime(d, '%Y-%m-%d') for d, _ in intro_vids]
intro_counts = [c for _, c in intro_vids]

# 按半年聚合
intro_by_period = defaultdict(int)
for d, c in intro_vids:
    half = '上' if int(d[5:7]) <= 6 else '下'
    key = f"{d[:4]}{half}"
    intro_by_period[key] += c
period_labels = sorted(intro_by_period.keys())
period_vals = [intro_by_period[k] for k in period_labels]

fig, ax = plt.subplots(figsize=(12, 5), dpi=200)
bars = ax.bar(period_labels, period_vals, color=PALETTE['teal'], width=0.6, edgecolor='white', linewidth=0.8, zorder=3)
for bar, val in zip(bars, period_vals):
    if val > 0:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(val),
                ha='center', va='bottom', fontsize=9, color=PALETTE['text'])
ax.set_ylabel('自我介绍次数', fontsize=12)
ax.set_title('「我是warma/沃玛」出现频率（按半年）', fontsize=14, fontweight='bold', pad=12)
plt.xticks(rotation=45, ha='right', fontsize=9)
style_ax(ax)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, '08_intro_freq.png'), bbox_inches='tight', facecolor='white')
plt.close(fig)
print('✓ 08_intro_freq.png')

# 输出统计摘要（供 HTML 仪表板使用）
stats = {
    'total_videos': len(vids),
    'total_sub_lines': data.get('total_sub_lines', sum(v.get('sub_lines',0) for v in vids)),
    'total_sub_chars': sum(v.get('sub_chars',0) for v in vids),
    'date_start': sorted_vids[0]['date'],
    'date_end': sorted_vids[-1]['date'],
    'yearly': {y: years_counter[y] for y in year_labels},
    'types': dict(type_counter.most_common()),
    'accounts': dict(acct_counter.most_common()),
}
with open(os.path.join(CHARTS, 'stats.json'), 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)
print('\n✓ stats.json')
print(f'\n共生成 8 张图表，保存在 {CHARTS}')
