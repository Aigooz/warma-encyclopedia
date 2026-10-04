# -*- coding: utf-8 -*-
from __future__ import annotations
import json, sys, urllib.request, urllib.parse, gzip, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'registry.json'
CACHE=ROOT/'tools/bili_meta_cache.json'
OUT=ROOT/'tools/bili_tid_names.json'
def main():
    sys.path.insert(0,str(ROOT/'tools'))
    from bili_api import _headers
    headers=_headers()
    reg=json.loads(REG.read_text(encoding='utf-8'))
    meta=json.loads(CACHE.read_text(encoding='utf-8'))
    byb={v.get('bvid'):v for v in reg.get('videos',[])}
    sample_by_tid={}
    for bvid,v in byb.items():
        m=meta.get(bvid) or {}
        tid=m.get('tid')
        if tid and tid not in sample_by_tid:
            sample_by_tid[tid]=bvid
    result={}
    if OUT.exists():
        try: result=json.loads(OUT.read_text(encoding='utf-8'))
        except Exception: result={}
    for tid,bvid in sample_by_tid.items():
        if result.get(tid): continue
        url='https://api.bilibili.com/x/web-interface/view/detail?'+urllib.parse.urlencode({'bvid':bvid})
        try:
            req=urllib.request.Request(url,headers=headers)
            with urllib.request.urlopen(req,timeout=20) as r:
                raw=r.read()
                if r.headers.get('Content-Encoding')=='gzip': raw=gzip.decompress(raw)
                obj=json.loads(raw.decode('utf-8'))
            name=(obj.get('data') or {}).get('View',{}).get('tname') or ''
            result[tid]=name
        except Exception as e:
            print('FAIL',tid,bvid,repr(e))
        time.sleep(0.2)
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(result)
if __name__=='__main__':
    main()
