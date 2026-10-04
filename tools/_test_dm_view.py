import asyncio
from bilibili_api import video
async def main():
    v=video.Video(bvid='BV1gs411o7XM')
    view=await v.get_danmaku_view(cid=5393022)
    print(view.get('count'), view.get('dm_seg'), view.get('state'), view.get('text'))
asyncio.run(main())
