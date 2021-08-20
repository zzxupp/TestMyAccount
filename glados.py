import requests,json,os

QW360_TOKEN = os.environ["QW360_TOKEN"]
GLADOS_COOKIE = os.environ["GLADOS_COOKIE"]
QQ = os.environ["QQ"]
QMSG_KEY = os.environ["QMSG_KEY"]
    
    
def qw360(QW360_TOKEN, message):
    response = requests.get('https://push.bot.qw360.cn/send/' + QW360_TOKEN + '?msg=' + message).json()
    if (response["status"]) != 1:
        print('qw360 推送失败')
    else:
        print('qw360 推送成功') 
        
        
def qmsg(qmsg_key, qq, message): 
    urls='https://qmsg.zendee.cn/send/' + qmsg_key   #私聊消息推送接口
    data = {
        "qq": qq,
        "msg": message
    }
    response = requests.post(urls,data=data).json()
    if int(response["code"] / 100) != 0:
        print('Qmsg酱 推送失败')
    else:
        print('Qmsg酱 推送成功')


def start(): 
    url= "https://glados.rocks/api/user/checkin"
    url2= "https://glados.rocks/api/user/status"
    origin = "https://glados.rocks"
    referer = "https://glados.rocks/console/checkin"
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
    payload={
        'token': 'glados_network'
    }
    checkin = requests.post(url,headers={'cookie': GLADOS_COOKIE ,'referer': referer,'origin':origin,'user-agent':useragent,'content-type':'application/json;charset=UTF-8'},data=json.dumps(payload))
    state =  requests.get(url2,headers={'cookie': GLADOS_COOKIE ,'referer': referer,'origin':origin,'user-agent':useragent})
   # print(res)

    if 'message' in checkin.text:
        mess = checkin.json()['message']
        if mess == '\u6ca1\u6709\u6743\u9650':
            print('cookie过期')
            return 'cookie过期'
        time = state.json()['data']['leftDays']
        time = time.split('.')[0]
        #print(time)
    return mess

        
def notice(time,sckey,sever,mess):
    if sever == 'off':
        requests.get('https://sc.ftqq.com/' + sckey + '.send?text='+mess+'，you have '+time+' days left')
    else:
        requests.get('https://sc.ftqq.com/' + sckey + '.send?text=通知没打开')
        
def main_handler(event, context):
  return start()

if __name__ == '__main__':
    mes = start()
    qmsg(QMSG_KEY, QQ, '@face=181@ GLaDOS - 签到提醒:\n' + mes)
    qw360(QW360_TOKEN, 'GLaDOS - 签到提醒:\n' + mes)
