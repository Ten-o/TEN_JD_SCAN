'''
#调用方法先引用：
from utils.jdsign import get_sign
print(get_sign("getCommentList",{"bizType":"1","content":"2","evaAuraVersion":22},"android","11.2.8"))
'''
import base64
import hashlib
import time
import random
import urllib.parse
import uuid
import json

string1 = "KLMNOPQRSTABCDEFGHIJUVWXYZabcdopqrstuvwxefghijklmnyz0123456789+/"
string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def randomstr(num):
    randomstr = ''.join(str(uuid.uuid4()).split('-'))[num:]
    return randomstr

def randomstr1(num):
    randomstr = ""
    for i in range(num):
        randomstr = randomstr + random.choice("abcdefghijklmnopqrstuvwxyz0123456789")
    return randomstr

def sign_core(inarg):
    key = b'80306f4370b39fd5630ad0529f77adb6'
    mask = [0x37, 0x92, 0x44, 0x68, 0xA5, 0x3D, 0xCC, 0x7F, 0xBB, 0xF, 0xD9, 0x88, 0xEE, 0x9A, 0xE9, 0x5A]
    array = [0 for _ in range(len(inarg))]
    for i in range(len(inarg)):
        r0 = int(inarg[i])
        r2 = mask[i & 0xf]
        r4 = int(key[i & 7])
        r0 = r2 ^ r0
        r0 = r0 ^ r4
        r0 = r0 + r2
        r2 = r2 ^ r0
        r1 = int(key[i & 7])
        r2 = r2 ^ r1
        array[i] = r2 & 0xff
    return bytes(array)

def base64Encode(string):
    return base64.b64encode(string.encode("utf-8")).decode('utf-8').translate(str.maketrans(string1, string2))

def base64Decode(string):
    return base64.b64decode(string.translate(str.maketrans(string1, string2))).decode('utf-8')

def randomeid():
    return 'eidAaf8081218as20a2GM%s7FnfQYOecyDYLcd0rfzm3Fy2ePY4UJJOeV0Ub840kG8C7lmIqt3DTlc11fB/s4qsAP8gtPTSoxu' % randomstr1(
        20)

def get_ep(jduuid : str=''):
    if not jduuid:
        jduuid = randomstr(16)
    # jduuid=base64Decode('EQHtZNG2CJu5CzcnCzu0CK==')
    # print(jduuid)
    ts = str(int(time.time() * 1000))
    bsjduuid = base64Encode(jduuid)
    # ts='1643792319938'
    area = base64Encode('%s_%s_%s_%s' % (
        random.randint(1, 10000), random.randint(1, 10000), random.randint(1, 10000), random.randint(1, 10000)))
    d_model = random.choice(['Mi11Ultra', 'Mi11', 'Mi10'])
    d_model = base64Encode(d_model)
    return '{"hdid":"JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=","ts":%s,"ridx":-1,"cipher":{"area":"%s","d_model":"%s","wifiBssid":"dW5hbw93bq==","osVersion":"CJS=","d_brand":"WQvrb21f","screen":"CtS1DIenCNqm","uuid":"%s","aid":"%s","openudid":"%s"},"ciphertype":5,"version":"1.2.0","appname":"com.jingdong.app.mall"}' % (
        int(ts) - random.randint(100, 1000), area, d_model, bsjduuid, bsjduuid, bsjduuid), jduuid, ts

def get_sign(functionId, body, client : str="android", clientVersion : str='11.2.8',jduuid : str='') -> dict:
    if isinstance(body,dict):#判断body数据类型是否为dict 是就转化为json
        d=body
        body=json.dumps(body)
    else:
        d=json.loads(body)

    if "eid" in d:
        eid=d["eid"]
    else:
        eid=randomeid()

    ep, suid, st = get_ep(jduuid)
    # print(ep)
    sv = random.choice(["102", "111", "120"])
    # sv = '102'
    all_arg = "functionId=%s&body=%s&uuid=%s&client=%s&clientVersion=%s&st=%s&sv=%s" % (
        functionId, body, suid, client, clientVersion, st, sv)
    #print(all_arg)
    back_bytes = sign_core(str.encode(all_arg))
    sign = hashlib.md5(base64.b64encode(back_bytes)).hexdigest()
    # print(sign)
    data={}
    data["data"]={"functionId":functionId,"body":body,"clientVersion":clientVersion,"client":client,"uuid":suid,"eid":eid,"ep":ep,"st":st,"sign":sign,"sv":sv}
    data["convertUrl"]='functionId=%s&body=%s&clientVersion=%s&client=%s&sdkVersion=31&lang=zh_CN&harmonyOs=0&networkType=wifi&oaid=%s&eid=%s&ef=1&ep=%s&st=%s&sign=%s&sv=%s' % (
        functionId,body, clientVersion, client, suid, eid, urllib.parse.quote(ep), st, sign, sv)
    data["url"]='https://api.m.jd.com?%s' % (data["convertUrl"])
    return data