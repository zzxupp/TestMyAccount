import os,re,json,requests,time,datetime,random
from bs4 import BeautifulSoup

USERNAME = os.environ["EUSERV_USERNAME"]
PASSWORD = os.environ["EUSERV_PASSWORD"]

PROXIES = {
    "http": "http://127.0.0.1:10809",
    "https": "http://127.0.0.1:10809"
}

EUSERV_MSG = ''
desp = ''  # 空值

def log(info: str):
    #print(info)
    global desp
    desp = desp + info + '\n'
    
def login(username, password) -> (str, requests.session):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/83.0.4103.116 Safari/537.36",
        "origin": "https://www.euserv.com"
    }
    url = "https://support.euserv.com/index.iphp"
    session = requests.Session()
    
    sess = session.get(url, headers=headers)
    sess_id = re.findall("PHPSESSID=(\\w{10,100});", str(sess.headers))[0]
    # 访问png
    png_url = "https://support.euserv.com/pic/logo_small.png"
    session.get(png_url, headers=headers)
    
    login_data = {
        "email": username,
        "password": password,
        "form_selected_language": "en",
        "Submit": "Login",
        "subaction": "login",
        "sess_id": sess_id
    }

    f = session.post(url, headers=headers, data=login_data)
    f.raise_for_status()
    if f.text.find('Hello') == -1 and f.text.find('Confirm or change your customer data here') == -1:
        return '-1', session
    # print(f.request.url)
    # sess_id = f.request.url[f.request.url.index('=') + 1:len(f.request.url)]
    return sess_id, session


def get_servers(sess_id, session) -> {}:
    d = {}
    url = "https://support.euserv.com/index.iphp?sess_id=" + sess_id
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/92.0.4515.159 Safari/537.36",
        "origin": "https://www.euserv.com"
    }
    f = session.get(url=url, headers=headers)
    f.raise_for_status()
    soup = BeautifulSoup(f.text, 'html.parser')
    for tr in soup.select('#kc2_order_customer_orders_tab_content_1 .kc2_order_table.kc2_content_table tr'):
        server_id = tr.select('.td-z1-sp1-kc')
        if not len(server_id) == 1:
            continue
        flag = True if tr.select('.td-z1-sp2-kc .kc2_order_action_container')[
                           0].get_text().find('Contract extension possible from') == -1 else False
        d[server_id[0].get_text()] = flag
    return d


def renew(sess_id, session, password, order_id) -> bool:
    url = "https://support.euserv.com/index.iphp"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/83.0.4103.116 Safari/537.36",
        "Host": "support.euserv.com",
        "origin": "https://support.euserv.com",
        "Referer": "https://support.euserv.com/index.iphp"
    }
    data = {
        "Submit": "Extend contract",
        "sess_id": sess_id,
        "ord_no": order_id,
        "subaction": "choose_order",
        "choose_order_subaction": "show_contract_details"
    }
    session.post(url, headers=headers, data=data)
    data = {
        "sess_id": sess_id,
        "subaction": "kc2_security_password_get_token",
        "prefix": "kc2_customer_contract_details_extend_contract_",
        "password": password
    }
    f = session.post(url, headers=headers, data=data)
    f.raise_for_status()
    if not json.loads(f.text)["rs"] == "success":
        return False
    token = json.loads(f.text)["token"]["value"]
    data = {
        "sess_id": sess_id,
        "ord_id": order_id,
        "subaction": "kc2_customer_contract_details_extend_contract_term",
        "token": token
    }
    session.post(url, headers=headers, data=data)
    time.sleep(random.randint(5,9))
    return True


def check(sess_id, session):
    print("Checking.......")
    d = get_servers(sess_id, session)
    flag = True
    for key, val in d.items():
        if val:
            flag = False
            log("ServerID: %s Renew Failed!" % key)
    if flag:
        log("ALL Work Done! Enjoy")
 
def main():
    today = datetime.datetime.today()
    if int(today.day) == 17:
        if not USERNAME or not PASSWORD:
            print("你没有添加任何账户")
            exit(1)
        user_list = USERNAME.strip().split()
        passwd_list = PASSWORD.strip().split()
        if len(user_list) != len(passwd_list):
            log("The number of usernames and passwords do not match!")
            exit(1)
        for i in range(len(user_list)):
            print('*' * 30)
            log("正在续费第 %d 个账号" % (i + 1))
            sessid, s = login(user_list[i], passwd_list[i])
            if sessid == '-1':
                log("第 %d 个账号登陆失败，请检查登录信息" % (i + 1))
                continue
            SERVERS = get_servers(sessid, s)
            log("检测到第 {} 个账号有 {} 台VPS，正在尝试续期".format(i + 1, len(SERVERS)))
            for k, v in SERVERS.items():
                if v:
                    if not renew(sessid, s, passwd_list[i], k):
                        log("ServerID: %s Renew Error!" % k)
                    else:
                        log("ServerID: %s has been successfully renewed!" % k)
                else:
                    log("ServerID: %s does not need to be renewed" % k)
            time.sleep(random.randint(5,15))
            check(sessid, s)
            time.sleep(random.randint(10,19))
        print('*' * 30)
    else:
        log("每月执行一次即可，不需要每天都续约哈！")
          
    
if __name__ != "__main__":
    main()
    EUSERV_MSG = '【Euserv任务简报】\n' + desp
