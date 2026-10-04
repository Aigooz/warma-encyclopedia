import requests
for cid in [35862675979,40469597886]:
 r=requests.get(f'https://comment.bilibili.com/{cid}.xml',headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.bilibili.com/'},timeout=15)
 print(cid,r.status_code,len(r.content),r.text.count('<d p='))
