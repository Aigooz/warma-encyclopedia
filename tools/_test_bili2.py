import asyncio
from bilibili_api import video
async def main():
    for bvid,cid,dm in [('BV1XqF6zJEMG',None,6351),('BV1gfGw6RE5p',None,6398)]:
      v=video.Video(bvid=bvid)
      info=await v.get_info()
      cids=[p['cid'] for p in info['pages']]
      dms=await v.get_danmakus(cid=cids[0])
      print(bvid,'duration',info['duration'],'pages',len(info['pages']),'cid',cids[0],'danmakus',len(dms),'stat',info['stat']['danmaku'])
asyncio.run(main())
