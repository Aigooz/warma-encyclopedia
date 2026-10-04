import asyncio, json
from bilibili_api import video

async def main():
    v=video.Video(bvid='BV1gs411o7XM')
    dms=await v.get_danmakus(cid=5393022)
    print('count',len(dms))
    for d in dms[:5]:
        print({'text':d.text,'dm_time':d.dm_time,'send_time':d.send_time,'mode':d.mode,'color':d.color,'weight':d.weight,'id':d.id_,'crc':d.crc32_id})
asyncio.run(main())
