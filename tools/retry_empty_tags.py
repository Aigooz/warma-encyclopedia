# -*- coding: utf-8 -*-
from __future__ import annotations
import json, sys, time, urllib.request, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'registry.json'
OUT=ROOT/'tools/bili_tags_cache.json'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
def main():
    sys.path.insert(0,str(ROOT/'tools'))
    from bili_api import _headers
    headers=_headers()
    registry=json.loads(REG.read_text(encoding='utf-8'))
    bvids=[]
    seen=set()
    for row in registry.get('videos',[]):
        b=row.get('bvid')
        if b and b not in seen:
            seen.add(b); bvids.append(b)
    cache=json.loads(OUT.read_text(encoding='utf-8'))
    todo=[b for b in bvids if not cache.get(b)]
    print('todo',len(todo))
    for i,b in enumerate(todo,1):
        url='https://api.bilibili.com/x/tag/archive/tags?'+urllib.parse.urlencode({'bvid':b})
        ok=False
        for attempt in range(5):
            try:
                req=urllib.request.Request(url,headers=headers)
                with urllib.request.urlopen(req,timeout=20) as r:
                    raw=r.read()
                    if r.headers.get('Content-Encoding')=='gzip': raw=__import__('gzip').decompress(raw)
                    obj=json.loads(raw.decode('utf-8'))
                if obj.get('code')!=0: raise RuntimeError(f"code={obj.get('code')} msg={obj.get('message')}")
                rows=[]
                for x in obj.get('data') or []:
                    name=(x.get('tag_name') or '').strip()
                    if name: rows.append({'id':x.get('tag_id'),'name':name})
                cache[b]=rows
                ok=True
                break
            except Exception as e:
                print('retry',i,b,attempt+1,repr(e))
                time.sleep(1.5*(attempt+1))
        if not ok: cache[b]=[]
        if i%10==0 or i==len(todo):
            OUT.write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding='utf-8')
            print(f'{i}/{len(todo)}')
        time.sleep(1.0)
    OUT.write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding='utf-8')
    print('done',sum(bool(v) for v in cache.values()),'/',len(cache))
if __name__=='__main__':
    main()
