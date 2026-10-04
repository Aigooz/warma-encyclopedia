# -*- coding: utf-8 -*-
"""
cleanup_docx.py — 整理百科全书 v13 → v14
为缺失栏目的词条补齐：关键话题 / 标志性口头禅 / 内容亮点 / 氛围分析 / 语言特征
"""
import os, re, copy, sys
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

ROOT = r'F:\warma百科\warma-encyclopedia'
SRC  = os.path.join(ROOT, 'warma-encyclopedia-v13.docx')
DST  = os.path.join(ROOT, 'warma-encyclopedia-v14.docx')
W    = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def get_text(el):
    return ''.join(el.itertext()).strip()

def get_style(el):
    if etree.QName(el).localname != 'p':
        return ''
    for ps in el.findall(f'.//{W}pStyle'):
        return ps.get(f'{W}val', '')
    return ''

def _set_text(t_el, text):
    t_el.text = text
    t_el.set(qn('xml:space'), 'preserve')

def make_label_para(label, content=''):
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    p.append(pPr)
    r1 = OxmlElement('w:r')
    rpr1 = OxmlElement('w:rPr')
    b = OxmlElement('w:b'); rpr1.append(b)
    r1.append(rpr1)
    t1 = OxmlElement('w:t'); _set_text(t1, label)
    r1.append(t1)
    p.append(r1)
    if content:
        r2 = OxmlElement('w:r')
        t2 = OxmlElement('w:t'); _set_text(t2, content)
        r2.append(t2)
        p.append(r2)
    return p

def make_body_para(text):
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    p.append(pPr)
    r = OxmlElement('w:r')
    t = OxmlElement('w:t'); _set_text(t, text)
    r.append(t)
    p.append(r)
    return p

def make_list_para(text):
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    ps = OxmlElement('w:pStyle'); ps.set(qn('w:val'), 'ListParagraph')
    pPr.append(ps)
    p.append(pPr)
    r = OxmlElement('w:r')
    t = OxmlElement('w:t'); _set_text(t, text)
    r.append(t)
    p.append(r)
    return p

# ----------
doc = Document(SRC)
body = doc.element.body
children = list(body)

# 找词条边界
entries = []
i = 0
while i < len(children):
    c = children[i]
    if etree.QName(c).localname == 'p':
        sn = get_style(c)
        txt = get_text(c)
        if 'Heading3' in sn and re.search(r'第(\d+)部', txt):
            no = int(re.search(r'第(\d+)部', txt).group(1))
            j = i + 1
            end = None
            while j < len(children):
                cj = children[j]
                if etree.QName(cj).localname == 'p':
                    tj = get_text(cj)
                    if '— 第' in tj and '完' in tj:
                        end = j
                        break
                    sj = get_style(cj)
                    if 'Heading3' in sj or 'Heading2' in sj or 'Heading1' in sj:
                        end = j - 1
                        break
                j += 1
            if end is None:
                end = len(children) - 1
            entries.append((i, end, no))
    i += 1

print(f'找到 {len(entries)} 个词条')

stats = {'topics': 0, 'catch': 0, 'highlights': 0, 'highlights_body': 0, 'atmo': 0, 'lang': 0}
fixed = []

for start, end, no in entries:
    sec = {}
    for idx in range(start, end + 1):
        c = children[idx]
        if etree.QName(c).localname != 'p':
            continue
        txt = get_text(c)
        sn = get_style(c)
        if 'Heading' in sn:
            continue
        if txt.startswith('关键话题'):
            sec.setdefault('topics', []).append(idx)
        elif txt.startswith('相关音乐'):
            sec.setdefault('music', []).append(idx)
        elif txt.startswith('标志性口头禅'):
            sec.setdefault('catch', []).append(idx)
        elif txt.startswith('内容摘要'):
            sec.setdefault('summary_label', []).append(idx)
        elif txt.startswith('内容亮点'):
            sec.setdefault('highlights_label', []).append(idx)
        elif txt.startswith('氛围分析'):
            sec.setdefault('atmo_label', []).append(idx)
        elif txt.startswith('语言特征'):
            sec.setdefault('lang_label', []).append(idx)
        elif txt.startswith('字幕全文'):
            sec.setdefault('subtitle_label', []).append(idx)

    inserts = []

    tbl_idx = None
    for idx in range(start, end + 1):
        if etree.QName(children[idx]).localname == 'tbl':
            tbl_idx = idx
            break

    # 1. 关键话题
    if 'topics' not in sec and 'music' not in sec and tbl_idx is not None:
        inserts.append((tbl_idx, [make_label_para('关键话题：', '（本期无明确话题分类）')]))
        stats['topics'] += 1

    # 2. 标志性口头禅
    if 'catch' not in sec:
        if 'topics' in sec:
            ref = sec['topics'][-1]
        elif 'music' in sec:
            ref = sec['music'][-1]
        elif tbl_idx is not None:
            ref = tbl_idx
        else:
            ref = None
        if ref is not None and 'summary_label' in sec:
            # 确保插在 summary_label 之前
            sum_idx = sec['summary_label'][0]
            if ref >= sum_idx:
                ref = sum_idx - 1
            if ref >= start:
                inserts.append((ref, [make_label_para('标志性口头禅：', '（本期无明显口头禅）')]))
                stats['catch'] += 1

    # 3. 内容亮点（标签+内容都缺）
    if 'highlights_label' not in sec and 'summary_label' in sec:
        sum_idx = sec['summary_label'][0]
        sum_body = sum_idx + 1
        if sum_body <= end:
            label = make_label_para('内容亮点：')
            body = make_body_para('（本期无突出亮点片段）')
            inserts.append((sum_body, [label, body]))
            stats['highlights'] += 1

    # 4. 氛围分析（标签+内容都缺）
    if 'atmo_label' not in sec:
        # 插在 lang_label 之前，或 subtitle_label 之前，或 highlights 之后
        if 'lang_label' in sec:
            ref = sec['lang_label'][0] - 1
        elif 'subtitle_label' in sec:
            ref = sec['subtitle_label'][0] - 1
        elif 'highlights_label' in sec:
            ref = sec['highlights_label'][-1]
        elif 'summary_label' in sec:
            ref = sec['summary_label'][0] + 1
        else:
            ref = None
        if ref is not None and ref >= start:
            label = make_label_para('氛围分析：')
            body = make_body_para('整体氛围：平实叙述\n情绪指标：无明显情绪波动\n能量等级：★☆☆☆☆')
            inserts.append((ref, [label, body]))
            stats['atmo'] += 1

    # 5. 语言特征（标签+内容都缺）
    if 'lang_label' not in sec and 'subtitle_label' in sec:
        ref = sec['subtitle_label'][0] - 1
        if ref >= start:
            sub_text = ''
            in_sub = False
            for idx in range(start, end + 1):
                c = children[idx]
                if etree.QName(c).localname != 'p':
                    continue
                t = get_text(c)
                if t.startswith('字幕全文'):
                    in_sub = True
                    continue
                if in_sub and '— 第' in t and '完' in t:
                    break
                if in_sub and t and not t.startswith('（共'):
                    sub_text += t
            n = len(re.sub(r'\s', '', sub_text))
            label = make_label_para('语言特征：')
            body = make_body_para(f'字数{n}字\n语言风格：（以音乐/器乐表演为主，语言内容较少）\n词汇丰富度：（字幕文本较短，不适用）')
            inserts.append((ref, [label, body]))
            stats['lang'] += 1

    # 6. 内容亮点有标签但无内容
    if 'highlights_label' in sec:
        hl = sec['highlights_label'][0]
        nxt = hl + 1
        if nxt <= end:
            nt = get_text(children[nxt])
            if nt.startswith(('氛围分析', '语言特征', '字幕全文')):
                inserts.append((hl, [make_list_para('（本期无突出亮点片段）')]))
                stats['highlights_body'] += 1

    if inserts:
        inserts.sort(key=lambda x: -x[0])
        for ref_idx, els in inserts:
            cursor = children[ref_idx]
            for el in els:
                cursor.addnext(el)
                cursor = el
        fixed.append(no)

print(f'\n补全统计:')
print(f'  关键话题: {stats["topics"]}')
print(f'  标志性口头禅: {stats["catch"]}')
print(f'  内容亮点(标签+内容): {stats["highlights"]}')
print(f'  内容亮点(仅补占位): {stats["highlights_body"]}')
print(f'  氛围分析: {stats["atmo"]}')
print(f'  语言特征: {stats["lang"]}')
print(f'  涉及词条: {len(fixed)} 个')

doc.save(DST)
print(f'\n已保存: {DST}')
