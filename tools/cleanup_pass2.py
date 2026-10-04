# -*- coding: utf-8 -*-
"""第二轮：为有相关音乐但缺关键话题的词条补上关键话题。"""
import os, re
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

ROOT = r'F:\warma百科\warma-encyclopedia'
DOCX = os.path.join(ROOT, 'warma-encyclopedia-v14.docx')
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def get_text(el): return ''.join(el.itertext()).strip()
def get_style(el):
    if etree.QName(el).localname != 'p': return ''
    for ps in el.findall(f'.//{W}pStyle'):
        return ps.get(f'{W}val', '')
    return ''
def _st(t, text):
    t.text = text; t.set(qn('xml:space'), 'preserve')

doc = Document(DOCX)
body = doc.element.body
children = list(body)

entries = []
i = 0
while i < len(children):
    c = children[i]
    if etree.QName(c).localname == 'p':
        sn = get_style(c); txt = get_text(c)
        if 'Heading3' in sn and re.search(r'第(\d+)部', txt):
            no = int(re.search(r'第(\d+)部', txt).group(1))
            j = i + 1; end = None
            while j < len(children):
                cj = children[j]
                if etree.QName(cj).localname == 'p':
                    tj = get_text(cj)
                    if '— 第' in tj and '完' in tj: end = j; break
                    sj = get_style(cj)
                    if 'Heading' in sj and j > i + 2: end = j - 1; break
                j += 1
            if end is None: end = len(children) - 1
            entries.append((i, end, no))
    i += 1

fixed = 0
for start, end, no in entries:
    has_topics = False
    music_idx = None
    tbl_idx = None
    for idx in range(start, end + 1):
        c = children[idx]
        if etree.QName(c).localname == 'tbl':
            if tbl_idx is None: tbl_idx = idx
            continue
        if etree.QName(c).localname != 'p': continue
        txt = get_text(c)
        if txt.startswith('关键话题'): has_topics = True
        if txt.startswith('相关音乐') and music_idx is None: music_idx = idx
    if not has_topics and music_idx is not None:
        # 在相关音乐之前（即TABLE之后）插入关键话题
        ref_idx = tbl_idx if tbl_idx is not None else music_idx - 1
        if ref_idx < start: ref_idx = start
        # 创建关键话题段落
        p = OxmlElement('w:p')
        pPr = OxmlElement('w:pPr'); p.append(pPr)
        r1 = OxmlElement('w:r')
        rpr1 = OxmlElement('w:rPr'); b = OxmlElement('w:b'); rpr1.append(b); r1.append(rpr1)
        t1 = OxmlElement('w:t'); _st(t1, '关键话题：'); r1.append(t1); p.append(r1)
        r2 = OxmlElement('w:r')
        t2 = OxmlElement('w:t'); _st(t2, '（音乐/翻唱类视频，无对白话题分类）'); r2.append(t2); p.append(r2)
        children[ref_idx].addnext(p)
        fixed += 1
        print(f'  第{no}部: 补了关键话题')

print(f'\n共修复 {fixed} 个词条')
doc.save(DOCX)
print(f'已保存: {DOCX}')
