import requests,re
url='https://api.bilibili.com/x/v1/dm/list.so?oid=5393022'
r=requests.get(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.bilibili.com/'},timeout=10)
xml=r.text
print('bytes',len(r.content),'chars',len(xml),'items',xml.count('<d p='), 'ends',xml[-50:])
print(xml[:250])
print(xml[-250:])
