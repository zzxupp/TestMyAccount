import json,os,re,requests

#from womail import WOMAIL_MSG
#from glados import GLADOS_MSG
from euserv import EUSERV_MSG
from bilibili import BILIBILI_MSG
from cloudmusic import CLOUDMUSIC_MSG
#from jegotrip import JEGOTRIP_MSG

QW360_TOKEN = os.getenv('QW360_TOKEN')
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

#qmsg(QMSG_KEY, QQ, WOMAIL_MSG + '\n\n' + GLADOS_MSG + '\n\n' + BILIBILI_MSG + '\n\n' + EUSERV_MSG + '\n\n' + CLOUDMUSIC_MSG + '\n\n' + JEGOTRIP_MSG)
qw360(QW360_TOKEN, BILIBILI_MSG + '\n\n' + EUSERV_MSG + '\n\n' + CLOUDMUSIC_MSG)
#qw360(QW360_TOKEN, WOMAIL_MSG + '\n\n' + GLADOS_MSG + '\n\n' + BILIBILI_MSG + '\n\n' + EUSERV_MSG + '\n\n' + CLOUDMUSIC_MSG + '\n\n' + JEGOTRIP_MSG)
#print(WOMAIL_MSG + '\n')
#print(GLADOS_MSG + '\n')
#print(BILIBILI_MSG + '\n')
#print(CLOUDMUSIC_MSG)
#print('沃邮箱 - 签到提醒:\n' + womail.WOMAIL_MSG + '\n\n' + 'GLaDOS - 签到提醒:\n' + glados.GLADOS_MSG)
