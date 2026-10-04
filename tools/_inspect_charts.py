from openpyxl import load_workbook
from pathlib import Path

files = [
    Path(r"F:\warma百科\@Warma 相关.xlsx"),
    Path(r"F:\warma百科\@warma养鸽场 相关.xlsx"),
]

for f in files:
    wb = load_workbook(f, data_only=False, read_only=False)
    print("\n", f.name)
    for ws in wb.worksheets:
        if ws._charts:
            print("sheet", ws.title, "charts", len(ws._charts))
            for i, chart in enumerate(ws._charts):
                print(" chart", i + 1, type(chart).__name__, chart.title)
                if chart.plots:
                    for s in chart.plots[0].series:
                        print("  series", s.tx.strRef.f if s.tx and s.tx.strRef else None, "val", s.val.numRef.f if s.val and s.val.numRef else None, "cat", s.cat.numRef.f if s.cat and s.cat.numRef else (s.cat.strRef.f if s.cat and s.cat.strRef else None))
    wb.close()
