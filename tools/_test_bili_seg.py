import asyncio
from bilibili_api import video
async def main():
    aid=116023005093755; cid=35862675979
    v=video.Video(aid=aid)
    for s in range(0,4):
      try:
       d=await v.get_danmakus(cid=cid,from_seg=s,to_seg=s)
       print('seg',s+1,'count',len(d),'first',d[0].dm_time if d else None,'last',d[-1].dm_time if d else None)
      except Exception as e: print('seg',s+1,'ERR',repr(e))
asyncio.run(main())
