import requests
for u in ['https://comment.bilibili.com/35862675979.json','https://comment.bilibili.com/35862675979.xml','https://comment.bilibili.com/35862675979/dmseg?segment=1']:
 r=requests.get(u,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.bilibili.com/'},timeout=15)
 print(u,r.status_code,len(r.content),r.content[:80])
