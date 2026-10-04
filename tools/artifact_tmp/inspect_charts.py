from pathlib import Path
from openpyxl import load_workbook

base = Path(r'F:\warma百科')
files = [base / '@Warma 相关.xlsx', base / '@warma养鸽场 相关.xlsx']
for fn in files:
    print('\n===', fn.name, '===')
    wb = load_workbook(fn, data_only=False, read_only=False)
    for ws in wb.worksheets:
        for ch in ws._charts:
            print(ws.title, 'chart', ch.title)
            for s in ch.series:
                print('  series', s)
            print('  anchor', ch.anchor._from.col, ch.anchor._from.row)
