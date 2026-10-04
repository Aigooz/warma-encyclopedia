import requests
for q in ['x/v2/dm/web/seg.so github','DmSegMobileReply proto','bilibili api dm seg.so pull_mode']:
    print('\nQ',q)
    r=requests.get('https://api.github.com/search/code',headers={'Accept':'application/vnd.github+json'},params={'q':q,'per_page':5},timeout=10)
    print(r.status_code,r.text[:1000])
