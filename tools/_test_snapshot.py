import asyncio, json
from bilibili_api import video
async def main():
 v=video.Video(aid=116023005093755)
 s=await v.get_danmaku_snapshot()
 print(json.dumps(s,ensure_ascii=False,indent=2))
asyncio.run(main())
