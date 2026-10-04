import requests,re
url='https://www.bilibili.com/video/BV1gs411o7XM/'
ua='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
html=requests.get(url,headers={'User-Agent':ua,'Cookie':'buvid3=1504863E-5468-5839-7204-05A802280AD550687infoc'},timeout=15).text
print('html chars',len(html),'dm refs',html.count('seg.so'))
urls=re.findall(r'https://(?:s1|s2|i0|static)\.hdslb\.com/[^"\']+',html)
print('scripts',len(urls))
for u in urls[:30]: print(u)
open('tools/_bili_page.html','w',encoding='utf-8').write(html)
