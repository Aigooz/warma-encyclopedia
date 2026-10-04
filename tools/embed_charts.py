# -*- coding: utf-8 -*-
"""
embed_charts.py — 将图表嵌入到百科 docx 中（v14 → v15）
在第一章概览（1.3 数据统计）之后插入数据可视化小节。
"""
import os, re
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = r'F:\warma百科\warma-encyclopedia'
SRC  = os.path.join(ROOT, 'warma-encyclopedia-v14.docx')
DST  = os.path.join(ROOT, 'warma-encyclopedia-v15.docx')
CHARTS = os.path.join(ROOT, 'charts')

doc = Document(SRC)

# 找到 "1.4 标志性口头禅与语言习惯" 这个 H2 的位置，在其前面插入可视化小节
target_heading = None
for p in doc.paragraphs:
    if p.style and p.style.name == 'Heading 2' and '1.4' in p.text:
        target_heading = p
        break

if target_heading is None:
    print("❌ 未找到 1.4 标题")
    exit(1)

print(f"✓ 找到插入点: [{target_heading.style.name}] {target_heading.text[:40]}")

# 在目标标题之前插入可视化小节
anchor = target_heading._p  # XML element

def insert_before(anchor_el, new_el):
    anchor_el.addprevious(new_el)

def make_heading2(text):
    """创建 Heading 2 段落"""
    p = doc.add_paragraph()
    # 移除默认添加到 body 末尾的段落
    doc.element.body.remove(p._p)
    p.style = doc.styles['Heading 2']
    p.text = text
    return p

def make_heading3(text):
    p = doc.add_paragraph()
    doc.element.body.remove(p._p)
    p.style = doc.styles['Heading 3']
    p.text = text
    return p

def make_body(text):
    p = doc.add_paragraph()
    doc.element.body.remove(p._p)
    run = p.add_run(text)
    return p

def make_image_para(img_path, width_cm=15.5, caption=None):
    """创建包含图片的段落"""
    p = doc.add_paragraph()
    doc.element.body.remove(p._p)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(img_path, width=Cm(width_cm))
    if caption:
        cap_p = doc.add_paragraph()
        doc.element.body.remove(cap_p._p)
        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap_run = cap_p.add_run(caption)
        cap_run.font.size = Pt(9)
        cap_run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
        cap_run.font.italic = True
    return p

# ---------- 插入 H2 标题 ----------
h2 = make_heading2('1.4 数据可视化')
insert_before(anchor, h2._p)
print('  ✓ 插入 H2 标题: 1.4 数据可视化')

# ---------- 图1: 年度投稿趋势 ----------
h3 = make_heading3('年度投稿趋势')
insert_before(anchor, h3._p)
make_body('以下图表展示了 warma 从 2015 年首次投稿到 2026 年的年度投稿数量变化。2019 年达到峰值（59 部），此后逐渐回落至每年 20-30 部的稳定更新节奏。')
insert_before(anchor, make_body('以下图表展示了 warma 从 2015 年首次投稿到 2026 年的年度投稿数量变化。2019 年达到峰值（59 部），此后逐渐回落至每年 20-30 部的稳定更新节奏。')._p)
img1 = make_image_para(os.path.join(CHARTS, '01_yearly_trend.png'), caption='图 1-1 年度投稿趋势（2015–2026）')
insert_before(anchor, img1._p)

# ---------- 图2: 内容类型分布 ----------
h3 = make_heading3('视频类型分布')
insert_before(anchor, h3._p)
make_body('内容类型环形图显示了各类型视频的占比。游戏实况和翻唱/音乐是两大核心内容，合计占比超过四分之一。')
insert_before(anchor, make_body('内容类型环形图显示了各类型视频的占比。游戏实况和翻唱/音乐是两大核心内容，合计占比超过四分之一。')._p)
img2 = make_image_para(os.path.join(CHARTS, '02_type_donut.png'), width_cm=14, caption='图 1-2 视频类型分布（共 318 部）')
insert_before(anchor, img2._p)

# ---------- 图3: 月度投稿热力图 ----------
h3 = make_heading3('月度投稿热力图')
insert_before(anchor, h3._p)
make_body('热力图以年份×月份矩阵展示投稿的时间分布，颜色越深表示当月投稿越多，可以清晰看到 warma 的活跃期和休更期。')
insert_before(anchor, make_body('热力图以年份×月份矩阵展示投稿的时间分布，颜色越深表示当月投稿越多，可以清晰看到 warma 的活跃期和休更期。')._p)
img3 = make_image_para(os.path.join(CHARTS, '03_monthly_heatmap.png'), caption='图 1-3 月度投稿热力图（颜色深浅表示投稿数量）')
insert_before(anchor, img3._p)

# ---------- 图4: 字幕累计增长 ----------
h3 = make_heading3('字幕累计增长')
insert_before(anchor, h3._p)
make_body('双轴折线图展示了字幕字数（万字符）和字幕行数（千行）的累计增长。2019-2020 年是字幕量增长最快的阶段。')
insert_before(anchor, make_body('双轴折线图展示了字幕字数（万字符）和字幕行数（千行）的累计增长。2019-2020 年是字幕量增长最快的阶段。')._p)
img4 = make_image_para(os.path.join(CHARTS, '04_subtitle_growth.png'), caption='图 1-4 字幕累计增长趋势')
insert_before(anchor, img4._p)

# ---------- 图5: 主号/小号分布 ----------
h3 = make_heading3('主号与小号投稿分布')
insert_before(anchor, h3._p)
make_body('Warma 目前使用主号（Warma）和小号（warma养鸽场、怒九摸鱼馆）两个账号进行投稿，主号仍占绝对多数。')
insert_before(anchor, make_body('Warma 目前使用主号（Warma）和小号（warma养鸽场、怒九摸鱼馆）两个账号进行投稿，主号仍占绝对多数。')._p)
img5 = make_image_para(os.path.join(CHARTS, '05_account_dist.png'), width_cm=13, caption='图 1-5 主号与小号投稿分布')
insert_before(anchor, img5._p)

# ---------- 图6: 投稿间隔 ----------
h3 = make_heading3('投稿间隔分析')
insert_before(anchor, h3._p)
make_body('散点图展示了每次投稿与上次投稿之间的间隔天数。大部分投稿间隔在一周以内，说明 warma 保持着较高的更新频率。')
insert_before(anchor, make_body('散点图展示了每次投稿与上次投稿之间的间隔天数。大部分投稿间隔在一周以内，说明 warma 保持着较高的更新频率。')._p)
img6 = make_image_para(os.path.join(CHARTS, '06_upload_gaps.png'), caption='图 1-6 投稿间隔分布（虚线为参考线）')
insert_before(anchor, img6._p)

# ---------- 图7: 字幕量TOP20 ----------
h3 = make_heading3('字幕量最多的视频')
insert_before(anchor, h3._p)
make_body('以下排名列出了字幕字数最多的 20 部视频，通常是大型直播录像或长篇实况内容。')
insert_before(anchor, make_body('以下排名列出了字幕字数最多的 20 部视频，通常是大型直播录像或长篇实况内容。')._p)
img7 = make_image_para(os.path.join(CHARTS, '07_top_subtitle.png'), width_cm=14.5, caption='图 1-7 字幕量最多的 20 部视频')
insert_before(anchor, img7._p)

# ---------- 图8: 自我介绍频率 ----------
h3 = make_heading3('「我是warma/沃玛」出现频率')
insert_before(anchor, h3._p)
make_body('按半年统计的自我介绍出现次数。2020 年下半年达到峰值（159 次），此后逐渐减少，说明 warma 越来越不需要自我介绍——粉丝已经认识她了。')
insert_before(anchor, make_body('按半年统计的自我介绍出现次数。2020 年下半年达到峰值（159 次），此后逐渐减少，说明 warma 越来越不需要自我介绍——粉丝已经认识她了。')._p)
img8 = make_image_para(os.path.join(CHARTS, '08_intro_freq.png'), caption='图 1-8 自我介绍频率变化（按半年）')
insert_before(anchor, img8._p)

# 更新原 1.4 标题编号为 1.5
target_heading.clear()
run = target_heading.add_run('1.5 标志性口头禅与语言习惯')

# 同时更新后续的 1.5 → 1.6
for p in doc.paragraphs:
    if p.style and p.style.name == 'Heading 2' and p.text.strip().startswith('1.5 创作里程碑'):
        p.clear()
        p.add_run('1.6 创作里程碑与粉丝增长')
        break

doc.save(DST)
print(f'\n✅ 已保存: {DST}')
print(f'   文件大小: {os.path.getsize(DST)/1024/1024:.1f} MB')
