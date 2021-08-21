# -*- encoding: utf-8 -*-
"""
@FILE    :   action.py
@DSEC    :   网易云音乐签到刷歌脚本
@AUTHOR  :   Secriy
@DATE    :   2020/08/25
@VERSION :   2.6
"""

import os, random, time, requests, base64, binascii, argparse, hashlib, json
from Crypto.Cipher import AES

CLOUDMUSIC_MSG = ''


# Get the arguments input.
# 用于获取命令行参数并返回dict
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("phone", help="Your Phone Number.")
    parser.add_argument("password", help="The plaint text or MD5 value of the password.")
    args = parser.parse_args()

    return {
        "phone": args.phone,
        "password": args.password
    }


# Calculate the MD5 value of text
# 计算字符串的32位小写MD5值
def calc_md5(text):
    md5_text = hashlib.md5(text.encode(encoding="utf-8")).hexdigest()
    return md5_text


# AES Encrypt
# 用于进行AES加密操作
def aes_encrypt(text, sec_key):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(sec_key.encode("utf8"), 2, b"0102030405060708")
    ciphertext = encryptor.encrypt(text.encode("utf8"))
    ciphertext = str(base64.b64encode(ciphertext), encoding="utf-8")
    return ciphertext


# RSA Encrypt
# 用于进行RSA加密
def rsa_encrypt(text, pub_key, modulus):
    text = text[::-1]
    rs = int(text.encode("utf-8").hex(), 16) ** int(pub_key, 16) % int(modulus, 16)
    return format(rs, "x").zfill(256)

# 加密类，实现网易云音乐前端加密流程
class Encrypt:
    def __init__(self):
        self.modulus = (
            "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629"
            "ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d"
            "813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7 "
        )
        self.nonce = "0CoJUm6Qyw8W8jud"
        self.pubKey = "010001"

    def encrypt(self, text):
        # Random String Generator
        sec_key = str(binascii.hexlify(os.urandom(16))[:16], encoding="utf-8")
        enc_text = aes_encrypt(aes_encrypt(text, self.nonce), sec_key)
        enc_sec_key = rsa_encrypt(sec_key, self.pubKey, self.modulus)
        return {"params": enc_text, "encSecKey": enc_sec_key}


# 网易云音乐类，实现脚本基础流程
class CloudMusic:
    def __init__(self, phone, password):
        self.session = requests.Session()
        self.enc = Encrypt()
        self.phone = phone
        self.csrf = ""
        self.nickname = ""
        self.uid = ""
        self.login_data = self.enc.encrypt(
            json.dumps({"username": phone, "password": password, "rememberLogin": "true"})
        )
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/86.0.4240.75 "
            "Safari/537.36",
            "Referer": "http://music.163.com/",
            "Accept-Encoding": "gzip, deflate",
        }

    # 登录流程
    def login(self):
        login_url = "https://music.163.com/weapi/login"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.38",
            "Referer": "http://music.163.com/",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": "os=pc; osver=Microsoft-Windows-10-Professional-build-10586-64bit; appver=2.0.3.131777; "
            "channel=netease; __remember_me=true;",
        }
        res = self.session.post(url=login_url, data=self.login_data, headers=headers)
        ret = json.loads(res.text)
        if ret["code"] == 200:
            self.csrf = requests.utils.dict_from_cookiejar(res.cookies)["__csrf"]
            self.nickname = ret["profile"]["nickname"]
            self.uid = ret["account"]["id"]
            level = self.get_level()
            text = '"{nickname}" 登录成功，当前等级：{level}\n\n距离升级还需听{count}首歌\n\n距离升级还需登录{days}天'.format(
                nickname=self.nickname,
                level=level["level"],
                count=level["nextPlayCount"] - level["nowPlayCount"],
                days=level["nextLoginCount"] - level["nowLoginCount"],
            )
        else:
            text = "账号 {0} 登录失败: ".format(self.phone) + str(ret["code"])
        return text

    # Get the level of account.
    # 获取用户的等级信息等
    def get_level(self):
        url = "https://music.163.com/weapi/user/level?csrf_token=" + self.csrf
        res = self.session.post(url=url, data=self.login_data, headers=self.headers)
        ret = json.loads(res.text)
        return ret["data"]

    # 执行用户的签到流程
    def sign(self, tp=0):
        sign_url = "https://music.163.com/weapi/point/dailyTask?{csrf}".format(csrf=self.csrf)
        res = self.session.post(url=sign_url, data=self.enc.encrypt('{{"type":{0}}}'.format(tp)), headers=self.headers)
        ret = json.loads(res.text)
        sign_type = "安卓端" if tp == 0 else "PC/Web端"
        if ret["code"] == 200:
            text = "{0}签到成功，经验+{1}".format(sign_type, str(ret["point"]))
        elif ret["code"] == -2:
            text = "{0}今天已经签到过了".format(sign_type)
        else:
            text = "签到失败 " + str(ret["code"]) + "：" + ret["message"]
        return text

    # 获取用户的推荐歌单
    def get_recommend_playlists(self):
        recommend_url = "https://music.163.com/weapi/v1/discovery/recommend/resource"
        res = self.session.post(
            url=recommend_url, data=self.enc.encrypt('{"csrf_token":"' + self.csrf + '"}'), headers=self.headers
        )
        ret = json.loads(res.text)
        playlists = []
        if ret["code"] == 200:
            playlists.extend([(d["id"]) for d in ret["recommend"]])
        else:
            print("获取推荐歌曲失败 " + str(ret["code"]) + "：" + ret["message"])
        return playlists

    # 获取用户的收藏歌单
    def get_subscribe_playlists(self):
        private_url = "https://music.163.com/weapi/user/playlist?csrf_token=" + self.csrf
        res = self.session.post(
            url=private_url,
            data=self.enc.encrypt(json.dumps({"uid": self.uid, "limit": 1001, "offset": 0, "csrf_token": self.csrf})),
            headers=self.headers,
        )
        ret = json.loads(res.text)
        subscribed_lists = []
        if ret["code"] == 200:
            for li in ret["playlist"]:
                if li["subscribed"]:
                    subscribed_lists.append(li["id"])
        else:
            print("个人订阅歌单获取失败 " + str(ret["code"]) + "：" + ret["message"])
        return subscribed_lists

    # 获取某一歌单内的所有音乐ID
    def get_list_musics(self, mlist):
        detail_url = "https://music.163.com/weapi/v6/playlist/detail?csrf_token=" + self.csrf
        musics = []
        for m in mlist:
            res = self.session.post(
                url=detail_url,
                data=self.enc.encrypt(json.dumps({"id": m, "n": 1000, "csrf_token": self.csrf})),
                headers=self.headers,
            )
            ret = json.loads(res.text)
            musics.extend([i["id"] for i in ret["playlist"]["trackIds"]])
        return musics

    # 获取任务歌单池内的所有音乐ID
    def get_task_musics(self):
        random.seed(time.time())
        musics = []
        recommend_musics = self.get_list_musics(self.get_recommend_playlists())
        subscribe_musics = self.get_list_musics(self.get_subscribe_playlists())
        musics.extend(random.sample(recommend_musics, 320) if len(recommend_musics) > 320 else recommend_musics)
        musics.extend(random.sample(subscribe_musics, 200) if len(subscribe_musics) > 200 else subscribe_musics)
        return musics

    # 任务
    def task(self):
        feedback_url = "http://music.163.com/weapi/feedback/weblog"
        post_data = json.dumps(
            {
                "logs": json.dumps(
                    list(
                        map(
                            lambda x: {
                                "action": "play",
                                "json": {
                                    "download": 0,
                                    "end": "playend",
                                    "id": x,
                                    "sourceId": "",
                                    "time": 240,
                                    "type": "song",
                                    "wifi": 0,
                                },
                            },
                            self.get_task_musics(),
                        )
                    )
                )
            }
        )
        res = self.session.post(url=feedback_url, data=self.enc.encrypt(post_data))
        ret = json.loads(res.text)
        if ret["code"] == 200:
            text = "刷听歌量成功"
        else:
            text = "刷听歌量失败 " + str(ret["code"]) + "：" + ret["message"]
        return text


# 执行任务，传递参数，推送结果
def run_task(phone, password):
    # 初始化
    app = CloudMusic(phone, password)
    # 登录
    res_login = app.login()
    print(res_login, end="\n\n")
    if "400" in res_login:
        print(res_login)
        print(30 * "=")
        return
    # PC/Web端签到
    res_sign = app.sign()
    print(res_sign, end="\n\n")
    # 安卓端签到
    res_m_sign = app.sign(1)
    print(res_m_sign, end="\n\n")
    # Music Task
    res_task = "刷听歌量失败"
    for i in range(1):
        res_task = app.task()
        print(res_task)
    print(30 * "=")
    # 推送
    message = res_login + "\n\n" + res_sign + "\n\n" + res_m_sign + "\n\n" + res_task
    print(30 * "=")
    return message

if __name__ != "__main__":
    CLOUDMUSIC_MSG = run_task('pingxuzheng@163.com', '53e77cd8fc7c1e5dba5aeab7cd1d3e52')
    
