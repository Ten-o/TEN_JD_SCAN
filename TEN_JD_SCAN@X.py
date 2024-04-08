# -*- coding: utf-8 -*-
"""
@author: 𝓣𝓮𝓷 𝓸'𝓬𝓵𝓸𝓬𝓴
@software: PyCharm
@file: TEN_JD_SCAN.py
@time: 2023/11/10 15:23
"""

import re
import json
import time
import uuid
import redis
import random
import asyncio
import aioredis
from utils.jdCookie import *
from utils.sign import get_sign
from utils.h5st import GET_H5ST
from utils.X_API_EID_TOKEN import *
from fake_useragent import UserAgent
from utils.MyApiClient import MyApiClient, log


class AsyncUrlStore:
    #去重数据库
    def __init__(self, host='', port=6379, db=0, password=''):
        self.redis_url = f'redis://{host}:{port}/{db}'
        self.password = password

    async def connect(self):
        self.redis = await aioredis.StrictRedis.from_url(
            self.redis_url,
            password=self.password,  # Provide the password here
        )

    async def close(self):
        await self.redis.aclose()

    async def add_url(self, url, url_set_key='url_set', url_sorted_set_key='url_sorted_set'):
        try:
            if not await self.redis.sismember(url_set_key, url):
                timestamp = int(time.time())
                async with self.redis.pipeline() as pipe:
                    pipe.sadd(url_set_key, url)
                    pipe.zadd(url_sorted_set_key, {url: timestamp})
                    await pipe.execute()
                    return True
            else:
                return False
        except Exception as e:
            log.error(e)
            return False

    async def get_recent_urls_with_timestamps(self, limit=100, url_sorted_set_key='url_sorted_set'):
        url_score_pairs = await self.redis.zrevrangebyscore(
            url_sorted_set_key, "+inf", "-inf", withscores=True, start=0, num=limit
        )
        urls_with_timestamps = [{"url": url, "timestamp": score} for url, score in url_score_pairs]
        return urls_with_timestamps


class Get_Body(object):
    def __init__(self, shopId, venderId):
        self.Get_Body = {
            'Get_Shop_Home-App': {
                "status": False,
                "mode": 'sign',
                "functionId": "getShopHomeFloorInfo",
                "url": 'https://api.m.jd.com/client.action?',
                # 'body': {
                #     "RNVersion": "0.59.9", "latWs": '', "lngWs": "", "source": "app-shop", "sourceRpc": "shop_app_home_allProduct",
                #     "displayWidth": "1053.000000", "navigationAbTest": "1", "lat": "", "shopId": shopId, "venderId": venderId,"lng": "",
                #     "refer": "app-search_searchList", "extend": ""}
                'body': {
                    "shopId": shopId, "source": "app-shop", "extend": "", "latWs": "", "lngWs": "",
                    "displayWidth": "1053.000000",
                    "sourceRpc": "shop_app_home_home", "lng": "", "lat": "", "navigationAbTest": "1"}
            },
            'Get_Shop_Home': {
                "status": True,
                "mode": 'h5st',
                "url": 'https://api.m.jd.com/client.action?',
                'body': {
                    "shopId": shopId,
                    "source": "m-shop"
                },
            },
            'Get_Shop_VipDetail': {
                "status": True,
                "mode": 'h5st',
                "url": 'https://api.m.jd.com/client.action?',
                'body': {
                    "sid": "",
                    "sr": "shopin",
                    "venderId": venderId,
                    "tabActive": "home-member",
                    "un_area": "19_1601_50283_62862",
                    "source": "app-shop"
                }
            },
            'Get_Shop_Popup': {
                "status": True,
                "mode": False,
                "url": 'https://api.m.jd.com/client.action?',
                'body': 'functionId=whx_getShopHomeActivityInfo&body=' + json.dumps({"shopId": shopId,
                                                                                     "source": "m-shop"}) + f'&t={int(round(time.time() * 1000))}&appid=shop_m_jd_com&clientVersion=11.0.0&client=wh5&area=1_72_2799_0&',
            },
            'Get_Shop_Popup-App': {
                "status": True,
                "mode": 'sign',
                "url": 'https://api.m.jd.com/client.action?',
                "functionId": "getShopHomeActivityInfo",
                "body": {
                    "shopId": shopId, "source": "app-shop", "latWs": "", "lngWs": "",
                    "displayWidth": "1053.000000", "sourceRpc": "shop_app_home_home",
                    "lng": "", "lat": "", "venderId": venderId
                }
            },

        }


class SCAN:
    def __init__(self):
        #config数据库
        self.pool = redis.ConnectionPool(host='', port=6379, decode_responses=True, db=1,
                                         password='')
        self.r = redis.Redis(connection_pool=self.pool)
        self.ua = UserAgent()
        self.lock = asyncio.Lock()
        self.ck = get_cookies()
        self.config = {}
        #tg反代
        self.tg_proxy = 'tg.ixu.cc'
        self.async_url_store = AsyncUrlStore()
        self.pro_url = []
        self.sale_url = []
        self.Black_Url_List = ['//coupon\.m\.jd\.com', '//item\.jd\.com.*html', '.*\.jpg.*', '.*\.mp4.*',
                               '.*wqdeal\.jd\.com.*', '.*\.png.*', '.*\.gif.*', '.*\.css.*', '.*\.js.*',
                               '.*memberApplyPopup.*', '//shopmember\.m\.jd\.com/shopcard?venderId=.*'
                                                       '//shop\.m\.jd\.com/?shopId=.*']
        self.headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'origin': 'https://shop.m.jd.com',
            'referer': 'https://shop.m.jd.com/',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': 'Windows',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'x-referer-page': 'https://shop.m.jd.com/shop/home',
            'x-rp-client': 'h5_1.0.0',
        }
        self.H5st_Config = {
            'Get_Shop_Home': {
                "functionId": "whx_getShopHomeFloorInfo",
                'appId': 'ea491',
                "appid": "shop_m_jd_com",
                "clientVersion": "12.0.0",
                "client": "wh5",
            },
            'Get_Shop_VipDetail': {
                "appId": '281e2',
                "functionId": "getVipDetail",
                "appid": "pages_jd_com",
                "clientVersion": "12.1.0",
                "client": "apple",
            },
            'Get_Shop_Member': {
                "appId": '9aa97',
                "functionId": "getFansFuseMemberDetail",
                "appid": "shopmember_m_jd_com",
                "clientVersion": "9.2.0",
                "client": "H5",
            },
        }

    async def get_mac_address(self):
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(5, -1, -1)])
        if mac not in self.config['MAC']:
            status, resp = await self.Requests('https://www.ip.cn/api/index?ip&type=0', 'ip', self.ua.safari, False)
            self.config['MAC'].update({mac: {'ip': resp['ip'], 'location': resp['address'], 'Semaphore': 50,
                                             'ShopId_list': 'select_shopId_5k', 'Proxy': 'proxy.aaaa.com:123456', }})

            await self.r.set('config', json.dumps(self.config))
        self.semaphore = asyncio.Semaphore(self.config['MAC'][mac]['Semaphore'])
        self.shopId_list = self.config['MAC'][mac]['ShopId_list']
        self.proxy = [self.config['MAC'][mac]['Proxy']]

    async def Requests(self, url, name, ua, proxy=True):
        self.headers.update({'user-agent': ua})
        opt = {
            'method': 'get',
            'name': name,
            'kwargs': {
                "url": url,
                "timeout": 10,
                "headers": self.headers,
            }
        }
        if name in ['Get_Shop_VipDetail']:
            opt['kwargs']['headers'].update({'Cookie': random.choice(self.ck)})
        if proxy and self.proxy:
            proxy = random.choice(self.proxy)
            opt['kwargs'].update({'proxy': 'http://' + proxy if 'http://' not in proxy else proxy})
        async with MyApiClient() as client:
            status, res = await client.sio_session(opt)
        return status, res

    async def GET_POST(self, url, index, name, ua, shopId):
        status, res = await self.Requests(url, name, ua)
        if status == 200 and 'code' in res and int(res['code']) not in [0, 200]:
            error_msg = "京东验证: 验证一下，购物无忧" if res and '验证一下，购物无忧' in str(res) else res
            log.error(
                "{:<8} {:<8} {:<11} {:<1}".format(f'[第{index}店铺]', f'[状态:{status}]',
                                                  f'[接口:{name}]',
                                                  f'[ERROR: {error_msg}]'))
        await self.Url_check(index, name, status, res, shopId)

    async def Get_H5st(self, name, body):
        opt = {
            "functionId": self.H5st_Config[name]['functionId'],
            'appId': self.H5st_Config[name]['appId'],
            "appid": self.H5st_Config[name]['appid'],
            "clientVersion": self.H5st_Config[name]['clientVersion'],
            "client": self.H5st_Config[name]['client'],
            "body": body,
        }
        h5st = await GET_H5ST(opt).Get_H5st()
        return h5st

    async def Get(self, index, shopId, venderId):
        data = Get_Body(shopId, venderId).Get_Body
        tasks = []
        for name in data:
            ua = self.ua.safari
            if not data[name]['status']:
                continue
            if data[name]['mode'] == 'h5st':
                h5st = await self.Get_H5st(name, data[name]['body'])
                if not h5st['code']:
                    return False
                ua = h5st['ua']
                body = h5st['body']
            elif data[name]['mode'] == 'sign':
                body = get_sign(data[name]['functionId'], data[name]['body'])['convertUrl']
            else:
                body = data[name]['body']
            task = asyncio.create_task(self.GET_POST(data[name]['url'] + body, index, name, ua, shopId))
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def SendText(self, msg, name, url, shopId):
        for i in self.config['chat_id']:
            localtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            opt = {
                'method': 'post',
                'name': 'SendText',
                'kwargs': {
                    'url': f'https://{self.tg_proxy}/bot{random.choice(self.config["TG_BOT_TOKEN"])}/sendMessage',
                    'timeout': 5,
                    "params": {
                        'chat_id': i,
                        'text': f'{msg}\n\n推送时间:{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}\n\nby:遥遥领先',
                        'disable_web_page_preview': 'true',
                        'parse_mode': "html",
                        'reply_markup': json.dumps({
                            "inline_keyboard": [
                                [
                                    {"text": "链接地址", "url": f"https://jump.ixu.cc/?url={url}"},
                                    {"text": "店铺地址", "url": f"https://shop.m.jd.com/?shopId={shopId}"}
                                ]
                            ]
                        })
                    },
                }
            }
            async with MyApiClient() as client:
                status, resp = await client.sio_session(opt)
            if not status:
                return False
            if resp['ok']:
                log.info(f'Telegram发送通知消息成功🎉。 当前时间{localtime}')
                return True
            elif resp['error_code']:
                log.error(f'telegram发送通知消息失败！！{resp}\n')
                return False

    async def Redis_check(self, url, name, shopId, t=0):
        msg = url
        type_match = re.findall('activityType=([\w]{5})', url, re.S)
        if type_match:
            if type_match[0] in self.config['loreal_type']:
                script = self.config['loreal_type'][type_match[0]]['script']
                msg = f'export {script}="{url}"'
                await self.async_url_store.add_url(url, script, script + '_set')
        else:
            for i in self.config['WX_type']:
                if re.findall(f'{i}', url, re.S):
                    script = self.config['WX_type'][i][f'variable']
                    msg = f'export ' + script + f'="{url}"'
                    await self.async_url_store.add_url(url, script, script + '_set')
        result = await self.async_url_store.add_url(url)
        if not result:
            return False
        while t < 3:
            t += 1
            SendText = await self.SendText(msg, name, url, shopId)
            if SendText:
                break

    async def Sale_mJdcom(self, url, index, shopId):
        try:
            async with self.lock:
                if url in self.sale_url:
                    return False
                self.sale_url.append(url)
            status, resp = await self.Requests(url, 'Sale_mJdcom', self.ua.safari)
            token = re.findall('token:\"(.*?)\"', resp, re.S)
            if token:
                project_id = re.findall('projectId:(.*?),', resp, re.S)[0].replace(' ', '')
                url = f'https://bigger.jd.com/m/content.json?projectId={project_id}&token={token[0]}'
                status, resp = await self.Requests(url, 'Sale_mJdcom', self.ua.safari)
                await self.Url_check(index, 'Sale_mJdcom', status, resp, shopId)
            else:
                log.error(f'Sale_mJdcom获取Token失败: {url}')
        except Exception as e:
            log.error(f'Sale_mJdcom: {e}')

    async def Pro_mJdcom(self, url, index, shopId):
        try:
            async with self.lock:
                if url in self.pro_url:
                    return False
                self.pro_url.append(url)
            if 'code' in url:
                return await self.Redis_check(url, 'Pro_mJdcom', shopId)

            status, resp = await self.Requests(url, 'Pro_mJdcom', self.ua.safari)
            if 'dVF7gQUVKyUcuSsVhuya5d2XD4F' in url:
                reurl = re.findall('\"activityCode\":\"(.*?)\"', resp.text, re.S)
                if reurl:
                    msg = 'export jd_pro_Invite=' + (f'"https://prodev.m.jd.com/mall/active'
                                                     f'/dVF7gQUVKyUcuSsVhuya5d2XD4F/index.html?code={reurl[0]}"')
                    await self.async_url_store.add_url(url, 'jd_pro_Invite', 'jd_pro_Invite_set')
                    result = await self.async_url_store.add_url(url)
                    if result:
                        await self.SendText(msg, 'Pro_mJdcom', url, shopId)
            else:
                await self.Url_check(index, 'Pro_mJdcom', status, resp, shopId, False)
        except Exception as e:
            log.error(f'Pro_mJdcom: {e} {url}')

    async def Url_check(self, index, name, status, resp, shopId, pro=True):
        if not status:
            return False
        regex = re.compile(r'//(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        url_result = re.findall(regex, str(resp))
        url_result = ["https:" + i.replace('\\', '').replace('amp;', '').replace('\'', '').replace(',',
                                                                                                   '') if "https:" not in i else i
                      for i in url_result]
        log.info(
            "{:<8} {:<8} {:<11} {:<1}".format(f'[第{index}店铺]', f'[状态:{status}]', f'[URL数量:{len(url_result)}]',
                                              f'[接口:{name}]'))

        for url in url_result:
            is_blacklisted = any(re.findall(black, url) for black in self.Black_Url_List)
            if is_blacklisted:
                continue
            if re.findall('m.jd.com/mall/active', url, re.S) and pro:
                return await self.Pro_mJdcom(url, index, shopId)
            elif re.findall("sale.jd.com", url, re.S):
                return await self.Sale_mJdcom(url, index, shopId)
            else:
                return await self.Redis_check(url, name, shopId)

    async def Task(self, index, shopId, venderId):
        async with self.semaphore:
            task = asyncio.create_task(self.Get(index, shopId, venderId))
            return await task

    async def Start(self):
        start = time.time()
        log.info("-" * 60)
        log.info("[从云端获取Config]")
        self.config = json.loads(self.r.get("config"))
        await self.get_mac_address()
        shopIds = self.r.hgetall(self.shopId_list)
        log.info(f"[云端获取到{len(shopIds)}个Id] [线程数:{self.semaphore._value}] [代理:{self.proxy}]")
        await self.async_url_store.connect()
        log.info("-" * 60)

        tasks = []
        for index, shopId in enumerate(shopIds, 1):
            shopInfo = json.loads(shopIds[shopId])
            task = asyncio.create_task(self.Task(index, shopInfo['shopId'], shopInfo['venderId']))
            tasks.append(task)
        await asyncio.gather(*tasks)
        log.info(f'Elapsed time: {int(round((time.time() - start) * 100)) / 100:.2f} seconds')


if __name__ == '__main__':
    while True:
        s = SCAN()
        asyncio.run(s.Start())
        time.sleep(5)
