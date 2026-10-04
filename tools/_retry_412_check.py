#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性检查：历史弹幕接口 412 是否解除。"""
import asyncio
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))

from bilibili_api import Credential, ResponseCodeException, video as bili_video

from fetch_history_danmaku import load_cookie_from_config, parse_cookie, protobuf_danmaku_records


async def main() -> None:
    cookie = parse_cookie(load_cookie_from_config())
    cred = Credential(
        sessdata=cookie.get("SESSDATA"),
        buvid3=cookie.get("buvid3"),
        bili_jct=cookie.get("bili_jct"),
        dedeuserid=cookie.get("DedeUserID"),
    )
    print("credential valid:", await cred.check_valid())
    api = bili_video.API["danmaku"]["get_history_danmaku"]
    params = {"oid": 5393022, "type": 1, "date": "20260901", "segment_index": 1}
    try:
        from bilibili_api import Api
        resp = await Api(api["url"], method=api["method"], wbi=True, verify=True,
                         credential=cred).update_params(**params).result
        recs = protobuf_danmaku_records(resp)
        print("OK records:", len(recs))
    except ResponseCodeException as exc:
        print("FAIL code:", exc.code, "body head:", (exc.raw or b"")[:120])
    except Exception as exc:  # noqa: BLE001
        code = getattr(exc, "code", "?")
        print("FAIL other code:", code, "type:", type(exc).__name__)


if __name__ == "__main__":
    asyncio.run(main())
