import configparser, asyncio, json
from pathlib import Path
from bilibili_api import Api, Credential
from bilibili_api import video as bili_video

ROOT = Path(r'F:\warma百科\warma-encyclopedia')
p = configparser.RawConfigParser(); p.read(ROOT/'config.ini', encoding='utf-8-sig')
cookie = next((p.get(s,'cookie').strip() for s in p.sections() if p.has_option(s,'cookie')), '')
parts = dict(x.strip().split('=',1) for x in cookie.replace('\n',';').split(';') if '=' in x)
cred = Credential(sessdata=parts.get('SESSDATA'), buvid3=parts.get('buvid3'), bili_jct=parts.get('bili_jct'), dedeuserid=parts.get('DedeUserID'))

async def main():
    cid = 42665262  # from old sample
    for wbi in (False, True):
        api = bili_video.API['danmaku']['get_history_danmaku_index']
        try:
            a = Api(url=api['url'], method='GET', wbi=wbi, verify=True, credential=cred).update_params(oid=cid, month='2026-09', type=1)
            r = await a.request(byte=True)
            print('wbi', wbi, 'ok bytes', len(r), r[:100])
        except Exception as e:
            print('wbi', wbi, type(e).__name__, repr(e))
asyncio.run(main())
