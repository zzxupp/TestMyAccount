import requests,json,os

PUSHPLUSTOKEN = os.environ["PUSHPLUS_TOKEN"]
qq = os.environ["QQ"]
qmsg_key = os.environ["QMSG_KEY"]
cookie = os.environ["COOKIE"]
    
    
def pushplus(token, title, content):
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": title,
        "content": content
    }
    body = json.dumps(data).encode(encoding='utf-8')
    headers = {'Content-Type': 'application/json'}
    rs = requests.post(url, data=body, headers=headers).json()
    if int(rs["code"] / 100) != 2:
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
    rs = requests.post(urls,data=data).json()
    if int(rs["code"] / 100) != 0:
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
    checkin = requests.post(url,headers={'cookie': cookie ,'referer': referer,'origin':origin,'user-agent':useragent,'content-type':'application/json;charset=UTF-8'},data=json.dumps(payload))
    state =  requests.get(url2,headers={'cookie': cookie ,'referer': referer,'origin':origin,'user-agent':useragent})
   # print(res)

    if 'message' in checkin.text:
        mess = checkin.json()['message']
        if mess == '\u6ca1\u6709\u6743\u9650':
            #requests.get('https://sc.ftqq.com/' + sckey + '.send?text=cookie过期')
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
    qmsg(qmsg_key, qq, '@face=181@ GLaDOS日志:\n' + mes)
    pushplus(PUSHPLUSTOKEN, 'GLaDOS日志', mes)
