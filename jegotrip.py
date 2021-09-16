import requests
import pprint
import os
import time

JEGOTRIP_MSG = ''

class JegoTrip():
    user_id: str

    def __init__(self, user_id):
        self.user_id = user_id

    def task(self):
        resp = requests.get(f'http://task.jegotrip.com.cn:8080/app/tasks?userid={self.user_id}')
        data = resp.json()
        #pprint.pprint(data)
        return data['rtn']['tasks']
    
    def sign(self, task_id) -> bool:
        resp = requests.post('http://task.jegotrip.com.cn:8080/app/sign',
                             json={
                                 'userid': self.user_id,
                                 'taskId': task_id    # 此处`I`要大写
                             },
                             headers={
                                 'Accept-Encoding': 'gzip, deflate',
                                 'Origin': 'http://task.jegotrip.com.cn:8080',
                                 'Accept': 'application/json, text/plain, */*',
                                 'Content-Type': 'application/json;charset=utf-8',
                                 'Connection': 'close',
                                 'Host': 'task.jegotrip.com.cn:8080',
                                 'Content-Length': '89',
                                 'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; MI 5 Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 Mobile Safari/537.36 source/jegotrip',
                                 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                                 'Referer': 'http://task.jegotrip.com.cn:8080/task/index.html'
                             })
        data = resp.json()
        #pprint.pprint(data)
        return data['result']
    
    def verify_result(self):
        tasks = self.task()
        for task in tasks.get('日常任务', []):
            if task.get('name') == '每日签到奖励':
                return True if task.get('triggerAction') == '已签到' else False

def getCoins():
        resp = requests.post('http://task.jegotrip.com.cn/api/service/user/v1/getUserTripCoins?lang=zh_CN&token=6d8b7e4204764e6cb953d8a859926007',
                             json={
                                 'page': '1',
                                 'pageSize': '30'    # 此处`I`要大写
                             },
                             headers={
                                 'Accept-Encoding': 'gzip, deflate, br',
                                 'Origin': 'https://app.jegotrip.com.cn',
                                 'Accept': '*/*',
                                 'X-Requested-With': 'XMLHttpRequest',
                                 'Sec-Fetch-Mode': 'cors',
                                 'Content-Type': 'application/json;charset=utf-8',
                                 'Connection': 'keep-alive',
                                 'Host': 'app.jegotrip.com.cn',
                                 'Content-Length': '26',
                                 'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; MI 5 Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 Mobile Safari/537.36 source/jegotrip',
                                 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                                 'Referer': 'https://app.jegotrip.com.cn/wyx/appwap/tripcoins/coinsHistory.html?token=6d8b7e4204764e6cb953d8a859926007&from=app'
                             })
        data = resp.json()
        pprint.pprint(data)
        return 'zzzz'

def readcredits(token, sign):
    timestamp = int(time.time())
    resp = requests.get(f'https://app1.jegotrip.com.cn/api/duiba/v1/mall/logonFree?token=6d8b7e4204764e6cb953d8a859926007&url=http://www.duiba.com.cn/autoLogin/autologin&timestamp={timestamp}&sign=6b59c1e812658c41f3f38099850ecf2346fdae73')
    data = resp.json()
    pprint.pprint(data)
    #_logonFreeUrl = data['body']['logonFreeUrl']
    #resqlist = _logonFreeUrl.split("&")
    #resqchar = resqlist[2]
    #pprint.pprint(resqchar)
    #return resqchar.split("=")[1]
    return 'zzz'

    
def main():
    _user_id = os.getenv('JEGOTRIP_USERID')
    _token = os.getenv('JEGOTRIP_TOKEN')
    _sign = os.getenv('JEGOTRIP_SIGN')
    checkin_state = ''
    cli = JegoTrip(_user_id)
    for task in cli.task().get('日常任务', []):
        if task.get('name') == '每日签到奖励':
            if task.get('triggerAction') == '签到':
                result = cli.sign(task['id'])
                if result:
                    checkin_state = '签到成功!'
                    if cli.verify_result() == False:
                        checkin_state = '签到失败:未知'
                    #print('签到成功!' if cli.verify_result() else '签到失败:未知')
            elif task.get('triggerAction') == '已签到':
                checkin_state = '今日已签到!'
    readcredits(_token,_sign)
    return f"{checkin_state}，当前无忧币的总数："
    #print(JEGOTRIP_MSG)

if __name__ == '__main__':
    main()
    #JEGOTRIP_MSG = f"【Jegotrip任务简报】\n{main()}"
