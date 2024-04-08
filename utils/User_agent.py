import random
import string
import json
import base64
import time
import uuid
from urllib.parse import quote




def generate_random_user_agent():
    # 随机生成iOS的操作系统版本
    ios_versions = ['13_3', '13_4', '13_5', '14_0', '14_1', '14_2', '14_3', '14_4', '15_0', '15_1', '15_2', '15_3', '15_4', '16_0', '16_1', '16_2', '16_3', '16_4']
    ios_version = random.choice(ios_versions)

    # 随机生成ep字段的值
    ep = {
        "ciphertype": 5,
        "cipher": {
            "ud": base64.b64encode(''.join(random.choices(string.ascii_letters + string.digits, k=32)).encode()).decode(),
            "sv": ''.join(random.choices(string.ascii_letters + string.digits, k=8)),
            "iad": ""
        },
        "ts": int(time.time()),
        "hdid": "ViZLFbOc+bY6wW3m9/8iSFjgglIbmHPOGSM9aXIoBes=",
        "version": "1.0.3",
        "appname": "com.360buy.jdmobile",
        "ridx": -1
    }
    # user_agent = f"jdltapp;iPhone;{random.randint(3, 8)}.{random.randint(0, 8)}.{random.randint(0, 8)};;;M/5.0;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;hasOCPay/0;appBuild/{random.randint(1000, 9999)};supportBestPay/0;jdSupportDarkMode/0;ef/1;ep/{ep_str};Mozilla/5.0 (iPhone; CPU iPhone OS {ios_version} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/{random.randint(10,50)}E{random.randint(100,500)};;supportJDSHWK/1;"

    # 生成User-Agent字符串
    user_agent = f"jdapp;iPhone;4.2.0;;;M/5.0;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;hasOCPay/0;appBuild/1217;supportBestPay/0;jdSupportDarkMode/0;ef/1;ep/{json.dumps(ep)};Mozilla/5.0 (iPhone; CPU iPhone OS {ios_version} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/{random.randint(10000,50000)};;supportJDSHWK/1;"
    return user_agent




