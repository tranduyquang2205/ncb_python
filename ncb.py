
import requests
import json
import time
import os
import hashlib
from datetime import datetime
import random
from bypass_ssl_v3 import get_legacy_session
import urllib3
PYPPETEER_CHROMIUM_REVISION = '1263111'
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION
import asyncio
import json
import random
import time 
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.cookies import RequestsCookieJar
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

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
        self.cookies_file = f"db/cookies/{account_number}.json"
        self.device_id = self.generate_device_id()
        self.session = requests.Session()
        self.load_cookies()
        self.cookies = RequestsCookieJar()

        self.access_token = ''
        
        self.osname = 'EDGE'
        self.osversion = '131.0.0.0'
        self.headers = {}
        
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
    def save_cookies(self,cookie_jar):
        with open(self.cookies_file, 'w') as f:
            json.dump(cookie_jar.get_dict(), f)
    def load_cookies(self):
        try:
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
                self.session.cookies.update(cookies)
                return
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return requests.cookies.RequestsCookieJar()
    def wait_for_page_load(self,driver, timeout=30):
        """Chờ đến khi trang tải xong."""
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    def get_cookies(self):
        cookie_dict = {}
        
        # Configure Chrome options
        options = uc.ChromeOptions()

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument('--headless=new')
        options.add_argument("--disable-dev-shm-usage") 
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
        options.add_argument("start-maximized")
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        options.add_argument(f'--user-agent={ua}')
        # options.headless = True
        
        # Set proxy if provided
        # if self.proxies:
        #     http_proxy = self.proxies.get('http')
        #     https_proxy = self.proxies.get('https')
        #     proxy_url = http_proxy or https_proxy  # Use either HTTP or HTTPS proxy
        #     proxy_parts = proxy_url.replace('http://', '').split('@')
        #     credentials, proxy_address = proxy_parts[0], proxy_parts[1]
        #     proxy_username, proxy_password = credentials.split(':')
        #     host, port = proxy_address.split(':')
        #     options.add_argument(f'--proxy-server=http://{proxy_username}:{proxy_password}@{host}:{port}')
        
        # Initialize undetected Chrome
        driver = uc.Chrome(options=options, enable_cdp_events=True)
        # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            
            driver.get("https://www.ncb-bank.vn")
            
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.has-menuchild:nth-child(5) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > a:nth-child(1)"))
            )
            self.wait_for_page_load(driver)
            # cookies = driver.get_cookies()
            # cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            # print(cookie_dict,len(cookie_dict))
            # self.session.cookies.update(cookie_dict)
            driver.get("https://www.ncb-bank.vn/nganhangso.khcn/gateway-server/personal-user-service/captcha")
            # Authenticate proxy if necessary
            # if self.proxies:
            #     driver.execute_script(f"window.open('about:blank', '_self').close();")  # Workaround for authentication popup
            #     driver.switch_to.window(driver.window_handles[0])
            #     driver.get(f'http://{proxy_username}:{proxy_password}@{host}:{port}')
            # time.sleep(50)
            # # Wait for the specific element (same as waitForSelector in Puppeteer)
            # WebDriverWait(driver, 30).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, ".f-title > p:nth-child(2)"))
            # )
            self.wait_for_page_load(driver)
            # logs = driver.get_log("performance")
            # cookies_dict = {}
            # for log in logs:
            #     log_data = json.loads(log["message"])["message"]
                
            #     if log_data["method"] == "Network.requestWillBeSent":
            #         request = log_data["params"]["request"]
            #         request_id = log_data["params"]["requestId"]  # Store request ID
                    
            #         if request["url"] == "https://www.ncb-bank.vn/nganhangso.khcn/gateway-server/personal-user-service/captcha":
            #             print("URL:", request["url"])
            #             print("Headers:", request["headers"])
                        
            #             # Try to get cookies from previous extra info event
            #             cookies = cookies_dict.get(request_id, "No cookies found")
            #             print("Cookies:", cookies)
                        
            #             self.headers = request["headers"]
            #             print("=" * 80)

            #     elif log_data["method"] == "Network.requestWillBeSentExtraInfo":
            #         request_id = log_data["params"]["requestId"]
                    
            #         # Extract cookies from this event
            #         cookies_list = log_data["params"].get("headers", {}).get("Cookie", None)
            #         if cookies_list:
            #             cookies_dict[request_id] = cookies_list
            
            cookies = driver.get_cookies()
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            
            self.session.cookies.update(cookie_dict)
            # print(cookie_dict)
            # time.sleep(5000)

            
        except Exception as e:
                print(f"Error: {e}")
        finally:
            if driver:
                driver.quit()
        return cookie_dict
          
    def login(self, captchaText,relogin=False):
        if not relogin and self.is_login and time.time() - self.time_login > 299:
            balance_response = self.get_balance(self.account_number)
            if balance_response['code'] != 500:
                return balance_response


        headers = {
        'authorization': 'Basic amF2YWRldmVsb3BlcnpvbmU6c2VjcmV0',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
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
        print('result',result)
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
                'priority': 'u=1, i',
                'referer': 'https://www.ncb-bank.vn/nganhangso.khcn/accounts',
                'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                }
            response = self.session.post(url, headers=headers, data=(data), proxies=self.proxies, verify=False)
            self.save_cookies(self.session.cookies)
            try:
                result = response.json()
            except:
                result = response.text
            return result
    def curl_get(self, url,headers = None):
            if not headers:
                headers = {
                'authorization': f'Bearer {self.access_token}',
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
                "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"'                }
            response = self.session.get(url, headers=headers, proxies=self.proxies, verify=False)
            self.save_cookies(self.session.cookies)
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

    def get_balance(self,account_number,retry=False):
        if not self.is_login or time.time() - self.time_login > 299:
            self.is_login = False
            self.save_data()
            login = self.handleLogin()
            if not login['success']:
                return login

        response = self.curl_get(self.url['account_info'](account_number))
        if response and 'code' in response and int(response['code']) == 200 and 'data' in response and response['data']:
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
        elif response and 'data' in response or not response['data']:
            return {'code':404,'success': False, 'message': 'account_number not found!'} 
        else: 
            self.is_login = False
            self.save_data()
            if not retry:
                return self.get_balance(account_number,retry=True)
            return {'code':520 ,'success': False, 'message': 'Unknown Error!','data':response} 

    def getCaptcha(self):
        if not self.session.cookies:
            self.session = requests.Session()
            print((self.get_cookies()))
        headers = {
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }
        # print(self.session.cookies)
        response = self.session.get(self.url['captcha'], headers=headers, proxies=self.proxies)
        self.save_cookies(self.session.cookies)
        try:
            response_json = response.json()
        except:
            self.session = requests.Session()
            return (response.text)
        return response_json["data"]['captchaAnswer']

    def get_transactions(self, account_number,from_date,to_date,page):
        if not self.is_login or time.time() - self.time_login > 299:
            self.is_login = False
            self.save_data()
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
            self.is_login = True
            self.save_data()
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
        print('captchaText',captchaText)
        session_raw = self.login(captchaText)
        return session_raw

