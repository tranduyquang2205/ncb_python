
import requests
import json
import time
import os
import hashlib
from datetime import datetime
import random
from bypass_ssl_v3 import get_legacy_session
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session_requests = get_legacy_session()

class NCB:
    def __init__(self,username, password, account_number, proxy_list=None):
        self.proxy_list = proxy_list
        self.url = {
            'captcha':'https://www.ncb-bank.vn/nganhangso.khcn/gateway-server/personal-user-service/captcha',
            'login':'https://www.ncb-bank.vn/nganhangso.khcn/gateway-server/oauth/token',
            'account_info': lambda account_number :f'https://www.ncb-bank.vn/nganhangso.khcn/gateway-server/personal-account-service/account/current/{account_number}?bnkid=&brncode=',
            'transactions': lambda account_number,from_date,to_date,page : f'https://www.ncb-bank.vn/nganhangso.khcn/gateway-server/personal-account-service/account/{account_number}/search?keyword=&fromDate={from_date}&toDate={to_date}&page={page}',
            'transactions_2': 'https://www.ncb-bank.vn/nganhangso.khcn/gateway-server/personal-account-service/dashboard/recent-transaction'
        }
        if self.proxy_list:
            self.proxy_info = self.proxy_list.pop(0)
            proxy_host, proxy_port, username_proxy, password_proxy = self.proxy_info.split(':')
            self.proxies = {
                'http': f'http://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}',
                'https': f'http://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}'
            }
        else:
            self.proxies = None
        
        self.password = password
        self.username = username
        self.account_number = account_number
        self.is_login = False
        self.file = f"db/users/{username}.txt"
        self.device_id = self.generate_device_id()
        self.session = requests.Session()
        
        self.osname = 'EDGE'
        self.osversion = '131.0.0.0'
        
        if not os.path.exists(self.file):
                    self.username = username
                    self.password = password
                    self.account_number = account_number
                    self.is_login = False
                    self.time_login = time.time()
                    self.save_data()
                    
        else:
            self.parse_data()
            self.username = username
            self.password = password
            self.account_number = account_number
    def save_data(self):
        data = {
            'username': self.username,
            'password': self.password,
            'account_number': self.account_number,
            'device_id': getattr(self, 'device_id', ''),
            'access_token': getattr(self, 'access_token', ''),
            'refresh_token': getattr(self, 'refresh_token', ''),
            'is_login':self.is_login,
            'time_login': self.time_login,
        }
        with open(self.file, 'w') as f:
            json.dump(data, f)

    def parse_data(self):
        with open(self.file, 'r') as f:
            data = json.load(f)
        self.username = data.get('username', '')
        self.password = data.get('password', '')
        self.account_number = data.get('account_number', '')
        self.device_id = data.get('device_id', '')
        self.access_token = data.get('access_token', '')
        self.refresh_token = data.get('refresh_token', '')
        self.is_login = data['is_login']
        self.time_login = data['time_login']
        
    def login(self, captchaText):
        headers = {
        'accept': 'application/json',
        'accept-language': 'vi',
        'authorization': 'Basic amF2YWRldmVsb3BlcnpvbmU6c2VjcmV0',
        'origin': 'https://www.ncb-bank.vn',
        'priority': 'u=1, i',
        'referer': 'https://www.ncb-bank.vn/nganhangso.khcn/dang-nhap',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
        }
        payload = {
                'username': self.username,
                'password': self.password,
                'captcha': captchaText,
                'grant_type': 'password',
                'grant_service': 'IB',
                'grant_device': self.device_id,
                'osname': self.osname,
                'osversion': self.osversion,
                'deviceid': self.device_id
        }

        
        result = self.curl_post(self.url['login'], headers=headers, data=(payload))
        
        if 'access_token' in result and result['access_token']:
            self.access_token = result['access_token']
            self.refresh_token = result['refresh_token']
            self.is_login = True
            self.save_data()
            
            return {
                'code': 200,
                'success': True,
                'message': "success",
                'access_token': self.access_token,
            }
        elif 'code' in result and result['code'] == 'INVALID-USER-PASS':
            return {
                'code': 444,
                'success': False,
                'message': result['description'],
                'data': result if result else ""
            }
        else:
            return {
                'code': 500,
                'success': False,
                'message': result['description'],
                "payload": payload,
                'data': result if result else ""
            }
    def curl_post(self, url, data,headers = None):
            if not headers:
                headers = {
                'accept': 'application/json',
                'accept-language': 'vi',
                'authorization': f'Bearer {self.access_token}',
                'origin': 'https://www.ncb-bank.vn',
                'priority': 'u=1, i',
                'referer': 'https://www.ncb-bank.vn/nganhangso.khcn/dang-nhap',
                'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
                }
            response = self.session.post(url, headers=headers, data=(data), proxies=self.proxies, verify=False)
            try:
                result = response.json()
            except:
                result = response.text
            return result
    def curl_get(self, url,headers = None):
            if not headers:
                headers = {
                'accept': 'application/json',
                'accept-language': 'vi',
                'authorization': f'Bearer {self.access_token}',
                'origin': 'https://www.ncb-bank.vn',
                'priority': 'u=1, i',
                'referer': 'https://www.ncb-bank.vn/nganhangso.khcn/dang-nhap',
                'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
                }
            response = self.session.get(url, headers=headers, proxies=self.proxies, verify=False)
            try:
                result = response.json()
            except:
                result = response.text
            return result
        
    def generate_device_id(self):
        timestamp = str(time.time_ns())
        # Hash the timestamp using SHA-256 and get the first 32 characters
        fingerprint = hashlib.sha256(timestamp.encode('utf-8')).hexdigest()[:32]
        return fingerprint
    def get_time_now(self):
        return datetime.now().strftime("%Y%m%d%H%M%S") 
    
    def generate_ref_no(self):
        return self.username +'-'+ self.get_time_now()+'-'+ str(random.randint(10000, 99999))

    def get_balance(self,account_number):
        if not self.is_login or time.time() - self.time_login > 299:
            login = self.handleLogin()
            if not login['success']:
                return login

        response = self.curl_get(self.url['account_info'](account_number))
            
        if 'code' in response and response['code'] == 200 and 'data' in response and response['data']:
                if float(response['data']['balance']) < 0 :
                    return {'code':448,'success': False, 'message': 'Blocked account with negative balances!',
                            'data': {
                                'balance':float(response['data']['balance'])
                            }
                            }
                else:
                    return {'code':200,'success': True, 'message': 'Thành công',
                            'data':{
                                'account_number':self.account_number,
                                'balance':float(response['data']['balance'])
                    }}
        elif 'data' in response or not response['data']:
            return {'code':404,'success': False, 'message': 'account_number not found!'} 
        else: 
            return {'code':520 ,'success': False, 'message': 'Unknown Error!','data':response} 

    def getCaptcha(self):
        
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'browser-id': '278254206',
            'content-type': 'application/json;charset=UTF-8',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
            }
        response = self.session.get(self.url['captcha'], headers=headers, proxies=self.proxies, verify=False)
        response_json = json.loads(response.text)
        return response_json["data"]['captchaAnswer']

    def get_transactions(self, account_number,from_date,to_date,page):
        if not self.is_login or time.time() - self.time_login > 299:
            login = self.handleLogin()
            if not login['success']:
                return login
        page=str(page)
        response = self.curl_get(self.url['transactions'](account_number,from_date,to_date,page))
        if 'code' in response and response['code'] == 200 and 'data' in response and response['data']:
            return {'code':200,'success': True, 'message': 'Thành công',
                            'data':{
                                'transactions':response['data']['content'],
                    }}
        elif 'code' in response and response['code'] == 6100:
            return {'code':404,'success': False, 'message': 'account_number not found!'} 
        else:
            return  {
                    "success": False,
                    "code": 500,
                    "data":response,
                    "message": "Unknow Error!"
                }
    def get_transactions_latest(self):
        if not self.is_login or time.time() - self.time_login > 299:
            login = self.handleLogin()
            if not login['success']:
                return login
        response = self.curl_get(self.url['transactions_2'])
        
        if 'code' in response and response['code'] == 200 and 'data' in response and response['data']:
            return {'code':200,'success': True, 'message': 'Thành công',
                            'data':{
                                'transactions':response['data'],
                    }}
        elif 'code' in response and response['code'] == 6100:
            return {'code':404,'success': False, 'message': 'account_number not found!'} 
        else:
            return  {
                    "success": False,
                    "code": 500,
                    "data":response,
                    "message": "Unknow Error!"
                }

    def handleLogin(self):
        captchaText = self.getCaptcha()
        session_raw = self.login(captchaText)
        return session_raw

