import json, csv, os, collections
jsonl='danmaku/all_danmaku.jsonl'
csvf='danmaku/all_danmaku.csv'
with open(jsonl,encoding='utf-8') as f:
    n=sum(1 for _ in f)
print('jsonl rows',n,'size',round(os.path.getsize(jsonl)/1024/1024,1),'MB')
with open(csvf,encoding='utf-8-sig',newline='') as f:
    r=csv.reader(f); header=next(r); rows=0
    for _ in r: rows+=1
print('csv rows',rows,'size',round(os.path.getsize(csvf)/1024/1024,1),'MB')
with open(jsonl,encoding='utf-8') as f:
    first=json.loads(next(f)); print('first keys',list(first.keys()))
    print('first sample',{k:first[k] for k in ['bvid','title','date','id','progress','mode','content']})
s=json.load(open('danmaku/summary.json',encoding='utf-8')); print('summary',s)
