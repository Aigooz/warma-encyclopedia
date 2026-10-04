import os
import asyncio
from bilibili_api import video, Credential
sess=os.getenv('BILI_SESSDATA','')
jct=os.getenv('BILI_JCT','')
dede=os.getenv('BILI_DEDE','')
buvid3=os.getenv('BILI_BUVID3','')
buvid4=os.getenv('BILI_BUVID4','')
async def main():
  for label,cred in [('no',None),('full',Credential(sessdata=sess,bili_jct=jct,dedeuserid=dede,buvid3=buvid3,buvid4=buvid4))]:
    v=video.Video(aid=116023005093755,credential=cred)
    try:
      info=await v.get_info(); print(label,'login info title',info['title'])
    except Exception as e: print(label,'info err',repr(e))
    try:
      d=await v.get_danmakus(cid=35862675979,from_seg=0,to_seg=0)
      print(label,'dms',len(d))
    except Exception as e: print(label,'dm err',repr(e))
asyncio.run(main())
