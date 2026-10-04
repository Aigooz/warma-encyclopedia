import requests,re,collections
xml=requests.get('https://comment.bilibili.com/35862675979.xml',headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.bilibili.com/'},timeout=15).text
items=re.findall(r'<d p="([^"]+)">(.*?)</d>',xml)
ps=[x[0].split(',') for x in items]
times=[float(p[0]) for p in ps]
ids=[p[7] for p in ps]
print('count',len(items),'time min/max',min(times),max(times),'unique ids',len(set(ids)))
print('modes',collections.Counter(int(p[1]) for p in ps))
print('weights',min(int(p[5]) for p in ps),max(int(p[5]) for p in ps))
print('first p',[','.join(p[:7]) for p in ps[:3]])
print('last p',[','.join(p[:7]) for p in ps[-3:]])
