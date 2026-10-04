import json,glob,os,collections
c=json.load(open('tools/bili_meta_cache.json',encoding='utf-8'))
expected={}
for bvid,v in c.items():
    for p in v.get('pages',[]):
        expected[(bvid,int(p['page']))]=(p['cid'],p.get('part',''),p.get('duration',0))
actual={(os.path.basename(f).split('.p')[0],int(os.path.basename(f).split('.p')[1].split('.')[0])) for f in glob.glob('danmaku/raw/*.p*.json')}
print('expected',len(expected),'actual',len(actual),'missing jobs',len(set(expected)-actual))
missing=sorted(set(expected)-actual)
print('missing',missing[:30])
print('dupes',[(k,v) for k,v in collections.Counter((bvid,int(p['page'])) for bvid,v in c.items() for p in v.get('pages',[])).items() if v>1][:10])
for bvid,page in missing:
    print('MISS',bvid,page,expected[(bvid,page)])
