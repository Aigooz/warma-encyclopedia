from openpyxl import load_workbook
from pathlib import Path

for f in [Path(r"F:\warma百科\@Warma 相关.xlsx"), Path(r"F:\warma百科\@warma养鸽场 相关.xlsx")]:
    wb = load_workbook(f, data_only=False, read_only=False)
    ws = wb["仪表盘"]
    print("\nFILE", f.name, "charts", len(ws._charts))
    for i, chart in enumerate(ws._charts):
        print("chart", i + 1, type(chart).__name__)
        print("series count", len(chart.series))
        for s in chart.series:
            print(" series", s)
            if hasattr(s, "val") and s.val:
                print(" val", s.val.numRef.f if s.val.numRef else None)
            if hasattr(s, "cat") and s.cat:
                print(" cat", s.cat.numRef.f if s.cat.numRef else (s.cat.strRef.f if s.cat.strRef else None))
    wb.close()
