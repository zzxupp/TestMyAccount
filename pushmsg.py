import json,os,re,requests
#import womail
#import glados
#import euserv
import bilibili

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

msg = 'bilibili.BiliBiliCheckIn(bilibili_cookie_list=_bilibili_cookie_list).main()'

qmsg(QMSG_KEY, QQ, BILIBILI_MSG)
qw360(QW360_TOKEN, msg)
qw360(QW360_TOKEN, BILIBILI_MSG)
#print('沃邮箱 - 签到提醒:\n' + womail.WOMAIL_MSG + '\n\n' + 'GLaDOS - 签到提醒:\n' + glados.GLADOS_MSG)
