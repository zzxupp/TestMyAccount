# -*- coding: utf-8 -*-

import json,os,re,requests

def pushplus(key,title,content):
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": key,
        "title": title,
        "content": content,
        "template": "json"
    }
    body = json.dumps(data).encode(encoding='utf-8')
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=body, headers=headers).json()
    if int(response["code"] / 100) != 2:
        print('PushPlus 推送失败')
    else:
        print('PushPlus 推送成功')

def qmsg(qmsg_key, qq, style): # style: msg,json,xml
    # urlg='https://qmsg.zendee.cn/group/' + qmsg_key  #群消息推送接口
    urls='https://qmsg.zendee.cn/send/' + qmsg_key   #私聊消息推送接口
    data = {
        "qq": qq,
        "msg": style
    }
    response = requests.post(urls,data=data).json()
    if int(response["code"] / 100) != 0:
        print('Qmsg酱 推送失败')
    else:
        print('Qmsg酱 推送成功')

class WoMailCheckIn:

    def __init__(self, check_item,lottery_url):
        self.check_item = check_item
        self.lottery_url = lottery_url
    @staticmethod

    def login(womail_url):
        try:
            url = womail_url
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; MI 5 Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.62 XWEB/2469 MMWEBSDK/200701 Mobile Safari/537.36 MMWEBID/3775 MicroMessenger/7.0.17.1701(0x27001141) Process/tools WeChat/arm64 GPVersion/1 NetType/WIFI Language/en ABI/arm64"
            }
            res = requests.get(url=url, headers=headers, allow_redirects=False)
            set_cookie = res.headers["Set-Cookie"]
            cookies = re.findall("YZKF_SESSION.*?;", set_cookie)[0]
            if "YZKF_SESSION" in cookies:
                return cookies
            else:
                print("沃邮箱获取 cookies 失败")
                return None
        except Exception as e:
            print("沃邮箱错误:", e)
            return None
    @staticmethod

    def dotask(cookies,lottery_url):
        global key
        msg = ""
        headers = {
            "User-Agent": "User-Agent: Mozilla/5.0 (Linux; Android 7.0; MI 5 Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.62 XWEB/2469 MMWEBSDK/200701 Mobile Safari/537.36 MMWEBID/3775 MicroMessenger/7.0.17.1701(0x27001141) Process/tools WeChat/arm64 GPVersion/1 NetType/WIFI Language/en ABI/arm64",
            "Cookie": cookies,
        }
        try:
            url = "https://nyan.mail.wo.cn/cn/sign/index/userinfo.do?rand=0.8897817905278955"
            res = requests.post(url=url, headers=headers)
            result = res.json()
            wxName = result.get("result").get("wxName")
            userMobile = result.get("result").get("userMobile")
            userdata = f"帐号信息: {wxName} - {userMobile[:3]}****{userMobile[-4:]}\n"
            msg += userdata
        except Exception as e:
            print("沃邮箱获取用户信息失败", e)
            msg += "沃邮箱获取用户信息失败\n"
        try:
            url = lottery_url
            response = requests.get(url, allow_redirects=False)
            cookies = {
                'JSESSIONID': re.findall("JSESSIONID=(.*?);", response.headers["Set-Cookie"])[0],
            }
            header = {
                'Content-Type': 'application/json;charset=UTF-8',
                'Referer': 'https://club.mail.wo.cn/ActivityWeb/scratchable/wap/template/index.html?activityId=387&resourceId=wo-wx'
            }
            data = '''{"activityId":"387"}'''
            for i in range(0):
                response = requests.post("https://club.mail.wo.cn/ActivityWeb/activity-function/get-prize-index", data=data,
                                     cookies=cookies, headers=header)
                msg += '自动抽奖：' + json.loads(response.text).get("description") + '\n'
        except Exception as e:
            print("自动抽奖:出错了",e)
            msg += "自动抽奖：出错了\n"
        try:
            url = "https://nyan.mail.wo.cn/cn/sign/user/checkin.do?rand=0.913524814493383"
            res = requests.post(url=url, headers=headers).json()
            result = res.get("result")
            if result == -2:
                msg += "每日签到: 已签到\n"
            elif result is None:
                msg += f"每日签到: 签到失败\n"
            else:
                msg += f"每日签到: 签到成功~已签到{result}天！\n"
        except Exception as e:
            print("沃邮箱签到错误", e)
            msg += "沃邮箱签到错误\n"

        try:
            url = "https://nyan.mail.wo.cn/cn/sign/user/doTask.do?rand=0.8776674762904109"
            data_params = {
                "每日首次登录手机邮箱": {"taskName": "loginmail"},
                "和WOWO熊一起寻宝": {"taskName": "treasure"},
                "去用户俱乐部逛一逛": {"taskName": "club"},
                "小积分抽大奖" : {"taskName" : "clubactivity"},
            }
            for key, data in dict.items(data_params):
                try:
                    res = requests.post(url=url, data=data, headers=headers).json()
                    result = res.get("result")
                    if result == 1:
                        msg += f"{key}: 做任务成功\n"
                    elif result == -1:
                        msg += f"{key}: 任务已做过\n"
                    elif result == -2:
                        msg += f"{key}: 请检查登录状态\n"
                    else:
                        msg += f"{key}: 未知错误\n"
                except Exception as e:
                    print(f"沃邮箱执行任务【{key}】错误", e)
                    msg += f"沃邮箱执行任务【{key}】错误"
        except Exception as e:
            print("沃邮箱执行任务错误", e)
            msg += "沃邮箱执行任务错误错误"
        return msg

    def main(self):
        womail_url = self.check_item.get("womail_url")
        canshu = womail_url.split("?")[1]
        self.lottery_url += canshu
        try:
            cookies = self.login(womail_url)
            if cookies:
                msg = self.dotask(cookies,self.lottery_url)
            else:
                msg = "登录失败"
        except Exception as e:
            print(e)
            msg = "登录失败"
        return msg

if __name__ == "__main__":
    _check_item = json.loads(os.getenv('WOMAIL_URL'))
    PUSHPLUSTOKEN = os.getenv('PUSHPLUS_TOKEN')
    QQ = os.environ["QQ"]
    QMSG_KEY = os.environ["QMSG_KEY"]
    _lottery_url = 'https://club.mail.wo.cn/ActivityWeb/activity-web/index?activityId=387&typeIdentification=scratchable&resourceId=wo-wx&'
    message = WoMailCheckIn(check_item=_check_item,lottery_url = _lottery_url).main()
    qmsg(QMSG_KEY, QQ, '@face=181@ 沃邮箱 - 签到提醒:\n' + message)
    pushplus(PUSHPLUSTOKEN, '沃邮箱 - 签到提醒', message)
    print(message)
