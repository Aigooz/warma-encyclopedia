import requests,re
for base,q in [('https://www.google.com/search?q=','site:github.com+x/v2/dm/web/seg.so'),('https://www.bing.com/search?q=','site:github.com%20x%2Fv2%2Fdm%2Fweb%2Fseg.so')]:
 r=requests.get(base+q,headers={'User-Agent':'Mozilla/5.0'},timeout=10); print('\n',base,r.status_code,len(r.text)); 
 for u in re.findall(r'https?://github\.com/[^\s"&]+',r.text)[:10]: print(u)
