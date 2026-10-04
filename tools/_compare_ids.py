import asyncio, re, requests
from bilibili_api import video
from bilibili_api.utils.BytesReader import BytesReader
UA='Mozilla/5.0'; TAB=[46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]
h={'User-Agent':UA,'Referer':'https://www.bilibili.com/'}
def wbi_url(params):
 nav=requests.get('https://api.bilibili.com/x/web-interface/nav',headers=h,timeout=10).json(); img=nav['data']['wbi_img']['img_url']; sub=nav['data']['wbi_img']['sub_url']; raw=re.sub(r'\.[a-zA-Z]+$','',img.rsplit('/',1)[-1])+re.sub(r'\.[a-zA-Z]+$','',sub.rsplit('/',1)[-1]); key=''.join(raw[i] for i in TAB)[:32]; p=dict(params); p['wts']=int(time.time()); p=dict(sorted(p.items())); q=urllib.parse.urlencode(p,quote_via=urllib.parse.quote); p['w_rid']=hashlib.md5((q+key).encode()).hexdigest(); return 'https://api.bilibili.com/x/v2/dm/wbi/web/seg.so?'+urllib.parse.urlencode(p)
async def main():
 v=video.Video(aid=116023005093755)
 d=await v.get_danmakus(cid=35862675979,from_seg=0,to_seg=0)
 print('seg dms',len(d),'ids unique',len(set(x.id_ for x in d)),'id_str unique',len(set(x.id_str for x in d)),'sample ids',[x.id_str or x.id_ for x in d[:5]])
 xml=requests.get('https://comment.bilibili.com/35862675979.xml',headers=h,timeout=15).text
 xitems=re.findall(r'<d p="([^"]+)">(.*?)</d>',xml)
 xmlids=[p.split(',')[7] for p,_ in xitems]
 print('xml dms',len(xitems),'unique ids',len(set(xmlids)),'sample',xmlids[:5])
 segids={str(x.id_str or x.id_) for x in d}
 print('intersection',len(segids & set(xmlids)),'xml only',len(set(xmlids)-segids),'seg only',len(segids-set(xmlids)))
asyncio.run(main())
