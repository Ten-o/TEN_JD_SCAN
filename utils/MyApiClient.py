# -*- coding: utf-8 -*-
"""
@author: 𝓣𝓮𝓷 𝓸'𝓬𝓵𝓸𝓬𝓴
@software: PyCharm
@file: MyApiClient.py
@time: 2023/11/3 16:16
"""


import aiohttp
import asyncio
import json
from utils.logger import setup_logger


log = setup_logger()


class MyApiClient:
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_session()

    async def _create_session(self):
        self.session = aiohttp.ClientSession()

    async def _close_session(self):
        if self.session:
            await self.session.close()


    async def request(self, method, kwargs):
        async with self.session.request(method, **kwargs) as response:
            status = response.status
            result = await response.text()
        if status == 200:
            try:
                result_json = json.loads(result)
            except:
                result_json = result
            return status, result_json
        else:
            return status, None

    async def sio_session(self, opt, t=0):
        if not self.session:
            await self._create_session()
        while t < 3:
            try:
                status, result = await self.request(opt['method'], opt['kwargs'])
                if status == 200:
                    return status, result
                else:
                    t += 1
                    log.debug(f'请求失败，第{t}次重试，状态: {status}，接口: {opt["name"]}')
            except asyncio.TimeoutError:
                t += 1
                log.debug(f'请求失败，第{t}次重试，状态: 请求超时，接口: {opt["name"]}')
            except Exception as e:
                t += 1
                log.debug(f'请求失败，第{t}次重试，状态: {e}，接口: {opt["name"]}')
        else:
            log.error(f'请求失败，大于3次，跳过该请求 接口: {opt["name"]}')
            return False, False
