import requests, re, hashlib, time, urllib.parse
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
TAB=[46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]
def headers(): return {'User-Agent':UA,'Referer':'https://www.bilibili.com/video/BV1XqF6zJEMG/'}
def wbi_url(params):
 nav=requests.get('https://api.bilibili.com/x/web-interface/nav',headers=headers(),timeout=10).json()
 img=nav['data']['wbi_img']['img_url']; sub=nav['data']['wbi_img']['sub_url']
 raw=re.sub(r'\.[a-zA-Z]+$','',img.rsplit('/',1)[-1])+re.sub(r'\.[a-zA-Z]+$','',sub.rsplit('/',1)[-1])
 key=''.join(raw[i] for i in TAB)[:32]
 p=dict(params); p['wts']=int(time.time()); p=dict(sorted(p.items()))
 q=urllib.parse.urlencode(p,quote_via=urllib.parse.quote)
 p['w_rid']=hashlib.md5((q+key).encode()).hexdigest()
 return 'https://api.bilibili.com/x/v2/dm/wbi/web/seg.so?'+urllib.parse.urlencode(p)
variants=[
 {'oid':35862675979,'type':1,'segment_index':1,'pid':116023005093755},
 {'oid':35862675979,'type':1,'segment_index':1,'pid':116023005093755,'pull_mode':1,'ps':0,'from':0},
 {'oid':35862675979,'type':1,'segment_index':1,'pid':116023005093755,'pull_mode':1},
]
for p in variants:
 r=requests.get(wbi_url(p),headers=headers(),timeout=15)
 print('params',p,'status',r.status_code,'bytes',len(r.content),'head',r.content[:80])
