import requests
import json

class SIGN(object):
    def __init__(self, username, password):
        self.__usr = username
        self.__pwd = password
        self.__session = requests.session()

    def __encrypt(self):
        url = "https://manage.71dj.com/common/routes/dc/transfer"
        data = "payload=" + self.__pwd
        self.__session.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.__encrypted = self.__session.post(url, data=data).json()['result'][0]

    def __login(self):
        url = "https://swjygw.71dj.com/saas/uaa/oauth/token"
        data = f"username={self.__usr}&grant_type=sms_code_and_password&client_id=dangjian-web&client_secret=dangjian-web-secret&password={self.__encrypted}&smscode=&gtOaCode="
        self.__session.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = self.__session.post(url, data=data).json()
        self.__access_token = resp['access_token']
        self.__userInfo = json.loads(resp['currentUserStr'])

    def __sign(self):
        url = "https://swjygw.71dj.com/saas/uc/api/cosign/log"
        self.__session.headers = {"Content-Type": "application/json;charset=UTF-8", "Authorization": "bearer " + self.__access_token}
        payload = {"unitId": self.__userInfo['currentUnitId'],"userId": self.__userInfo['id']}
        self.__result = self.__session.post(url, data=json.dumps(payload)).json()['msg']

    def run(self):
        print("--started--")
        self.__encrypt()
        print("encrypted:", self.__encrypted)
        self.__login()
        print("token:", self.__access_token)
        self.__sign()
        print("result:", self.__result)
        print("--finished--")

if __name__ == '__main__':

    SIGN("身份证号码", "密码").run()
