import os
import asyncio, datetime
from bilibili_api import video, Credential
sess=os.getenv('BILI_SESSDATA','')
jct=os.getenv('BILI_JCT',''); dede=os.getenv('BILI_DEDE',''); buvid3=os.getenv('BILI_BUVID3','')
async def main():
 v=video.Video(aid=116023005093755,credential=Credential(sessdata=sess,bili_jct=jct,dedeuserid=dede,buvid3=buvid3))
 for dt in [datetime.date(2026,2,8), datetime.date(2026,2,9), datetime.date(2026,2,10)]:
   try:
     idx=await v.get_history_danmaku_index(cid=35862675979,date=dt)
     print('idx',dt,idx)
     d=await v.get_danmakus(cid=35862675979,date=dt)
     print('dms',dt,len(d))
   except Exception as e: print('ERR',dt,repr(e))
asyncio.run(main())
