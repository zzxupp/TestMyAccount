import requests,json,os

GLADOS_COOKIE = os.environ["GLADOS_COOKIE"]  
GLADOS_MSG = ''

def start(): 
    url= "https://glados.rocks/api/user/checkin"
    url2= "https://glados.rocks/api/user/status"
    origin = "https://glados.rocks"
    referer = "https://glados.rocks/console/checkin"
    useragent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.112 Safari/537.36"
    payload={
        'token': 'glados_network'
    }
    checkin = requests.post(url,headers={'cookie': GLADOS_COOKIE ,'referer': referer,'origin':origin,'user-agent':useragent,'content-type':'application/json;charset=UTF-8'},data=json.dumps(payload))
    state =  requests.get(url2,headers={'cookie': GLADOS_COOKIE ,'referer': referer,'origin':origin,'user-agent':useragent})
   # print(res)

    if 'message' in checkin.text:
        mess = checkin.json()['message']
        if mess == '\u6ca1\u6709\u6743\u9650':
            return 'cookie过期'
    return mess
        
def main_handler(event, context):
  return start()

if __name__ != '__main__':
    GLADOS_MSG =  '【GlaDOS任务简报】\n' + start() + '\n'

