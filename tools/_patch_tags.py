from pathlib import Path
p=Path('tools/fetch_bili_tags.py')
s=p.read_text(encoding='utf-8')
s=s.replace("import json, time, urllib.request, urllib.parse, gzip\nfrom pathlib import Path\n", "import json, time, sys, urllib.request, urllib.parse, gzip\nfrom pathlib import Path\n")
s=s.replace("HEADERS = {\n    'User-Agent': UA,\n    'Referer': 'https://www.bilibili.com/',\n    'Origin': 'https://www.bilibili.com',\n    'Accept': 'application/json, text/plain, */*',\n    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',\n    'Accept-Encoding': 'gzip, deflate',\n}", "HEADERS = None\n")
s=s.replace("def main():\n    registry = json.loads(REG.read_text(encoding='utf-8'))", "def main():\n    sys.path.insert(0, str(ROOT / 'tools'))\n    from bili_api import _headers\n    global HEADERS\n    HEADERS = _headers()\n    registry = json.loads(REG.read_text(encoding='utf-8'))")
p.write_text(s,encoding='utf-8')
print('patched')
