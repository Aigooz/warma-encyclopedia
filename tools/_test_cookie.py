import requests, os
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
for name, cookie in [('env',os.getenv('BILI_COOKIES','')),('sess','SESSDATA_REPLACE_ME'),('none','')]:
    r=requests.get('https://api.bilibili.com/x/web-interface/nav',headers={'User-Agent':UA,'Referer':'https://www.bilibili.com/','Cookie':cookie},timeout=10)
    j=r.json(); print(name, j.get('code'), j.get('data',{}).get('isLogin'), len(r.content))
