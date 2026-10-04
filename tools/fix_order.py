# -*- coding: utf-8 -*-
"""fix_order.py — 检查并修正词条内栏目顺序"""
import os, re
from docx import Document
from lxml import etree

ROOT = r'F:\warma百科\warma-encyclopedia'
DOCX = os.path.join(ROOT, 'warma-encyclopedia-v14.docx')
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PRIORITY_INV = {0:'关键话题',1:'相关音乐',2:'标志性口头禅',3:'内容摘要',5:'内容亮点',7:'氛围分析',9:'语言特征',11:'字幕全文'}

def get_text(el): return ''.join(el.itertext()).strip()
def get_style(el):
    if etree.QName(el).localname != 'p': return ''
    for ps in el.findall(f'.//{W}pStyle'): return ps.get(f'{W}val', '')
    return ''
def classify(txt):
    if txt.startswith('关键话题'): return 0
    if txt.startswith('相关音乐'): return 1
    if txt.startswith('标志性口头禅'): return 2
    if txt.startswith('内容摘要'): return 3
    if txt.startswith('内容亮点'): return 5
    if txt.startswith('氛围分析'): return 7
    if txt.startswith('语言特征'): return 9
    if txt.startswith('字幕全文'): return 11
    return None

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

print(f'词条总数: {len(entries)}')
wrong = []
for start, end, no in entries:
    labels = []
    for idx in range(start + 1, end + 1):
        c = children[idx]
        if etree.QName(c).localname != 'p': continue
        txt = get_text(c)
        p = classify(txt)
        if p is not None:
            labels.append((idx, p))
    vals = [p for _, p in labels]
    if vals != sorted(vals):
        wrong.append((start, end, no, vals))
        print(f'  第{no}部: 顺序 {[PRIORITY_INV.get(p,p) for p in vals]}')

print(f'\n顺序错误的词条: {len(wrong)} 个')

for start, end, no, vals in wrong:
    segments = children[start+1:end]
    decorated = []
    prev = -1
    for orig_i, el in enumerate(segments):
        tag = etree.QName(el).localname
        if tag == 'tbl':
            p = -1
        else:
            txt = get_text(el)
            p = classify(txt)
            if p is None:
                if prev == 3: p = 4
                elif prev == 5: p = 6
                elif prev == 7: p = 8
                elif prev == 9: p = 10
                elif prev == 11: p = 12
                else: p = 99
            if p is not None and p < 90:
                prev = p
        decorated.append((p, orig_i, el))
    decorated.sort(key=lambda x: (x[0], x[1]))
    for el in segments:
        if el.getparent() is not None:
            body.remove(el)
    end_el = children[end] if end < len(children) else None
    # 重新获取 end 元素引用
    for _, _, el in decorated:
        # 插在 — 第N部完 — 之前
        # 找 end_el（它没有被移除，仍在 body 中）
        pass
    # 直接用 body 中当前 — 第N部完 — 位置
    # 由于我们移除了 segments，end 位置偏移了，但 children[end] 引用仍然有效
    end_el = children[end]
    for _, _, el in decorated:
        end_el.addprevious(el)

print('修正完成')
doc.save(DOCX)
print(f'已保存: {DOCX}')
