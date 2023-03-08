import requests
import json

class SIGN(object):
    def __init__(self, username, password):
        self.__usr = username
        self.__pwd = password
        self.__session = requests.session()

    def __host(self):
        """
        获取用户所在的组织域名, 实现支持其他单位
        :return:
        """
        url = "https://manage.71dj.com/common/routes/dc?login=" + self.__usr
        self.__hosted = self.__session.get(url).json()['result']

    def __encrypt(self):
        """
        获取加密后的密码
        :return:
        """
        url = "https://manage.71dj.com/common/routes/dc/transfer"
        data = "payload=" + self.__pwd
        self.__session.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.__encrypted = self.__session.post(url, data=data).json()['result'][0]

    def __login(self):
        """
        登录
        :return:
        """
        url = self.__hosted + "/saas/uaa/oauth/token"
        data = f"username={self.__usr}&grant_type=sms_code_and_password&client_id=dangjian-web&client_secret=dangjian-web-secret&password={self.__encrypted}&smscode=&gtOaCode="
        self.__session.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = self.__session.post(url, data=data).json()
        userStr = json.loads(resp['currentUserStr'])
        self.__unitId = str(userStr['currentUnitId'])
        self.__userId = str(userStr['id'])
        self.__access_token = resp['access_token']

    def __sign(self):
        """
        签到
        :return:
        """
        url = self.__hosted + "/saas/uc/api/cosign/log"
        self.__session.headers = {"Content-Type": "application/json;charset=UTF-8", "Authorization": "bearer " + self.__access_token}
        payload = {"unitId": self.__unitId,"userId": self.__userId}
        self.__result = self.__session.post(url, data=json.dumps(payload)).json()['msg']

    def __app(self):
        """
        生活服务
        :return:
        """
        url = self.__hosted + "/saas/score/api/score/life-service-click/report"
        self.__session.headers = {"Content-Type": "application/json;charset=UTF-8", "Authorization": "bearer " + self.__access_token}
        payload = {"url": "快递查询"}
        for item in range(2):
            self.__result = self.__session.post(url, data=json.dumps(payload)).json()['msg']

    def __red(self):
        """
        红土地动态发布/点赞/评论
        逻辑更改: 为什么不自己发, 自己赞, 自己评, 自己删呢?
        :return:
        """
        self.__session.headers = {"Content-Type": "application/json;charset=utf-8", "Authorization": "bearer " + self.__access_token}
        for item in range(2):
            url = "https://manage.71dj.com/saas/mgt/api/content/moments/new"  # 发布动态
            payload = {"content": "已学习", "showType": 0, "pubType": 1, "picKey": ""}
            self.__result = self.__session.post(url, data=json.dumps(payload)).json()['result']

            url = "https://manage.71dj.com/saas/mgt/api/common/operation/new" # 点赞
            payload = {"userId":self.__userId,"unitId":"","type":"10150014","businessId":self.__result}
            self.__session.post(url, data=json.dumps(payload))

            url = "https://manage.71dj.com/saas/mgt/api/common/comment/new" # 评论
            payload = {"body": "已学习", "businessType": "10150033", "unitId": self.__unitId, "userId": self.__userId, "businessId": self.__result, "commentImages": []}
            self.__session.post(url, data=json.dumps(payload))

            url = "https://manage.71dj.com/saas/mgt/api/content/moments/remove/" + self.__result # 删除动态
            self.__result = self.__session.post(url).json()['msg']

    def __faq(self):
        """
        问题答案点赞/收藏
        :return:
        """
        url = "https://manage.71dj.com/saas/mgt/api/content/question/listRecommendQuestion?page=1&pageSize=2"
        self.__session.headers = {"Content-Type": "application/json;charset=utf-8", "Authorization": "bearer " + self.__access_token}
        self.__result = self.__session.get(url).json()['result']['records']
        for item in self.__result:
            url = f"https://manage.71dj.com/saas/mgt/api/content/answer/listAnswers/{item['id']}?page=1&pageSize=2"
            self.__session.headers = {"Content-Type": "application/json;charset=utf-8", "Authorization": "bearer " + self.__access_token}
            self.__result = self.__session.get(url).json()['result']['records']
            for sub in self.__result:
                url = "https://manage.71dj.com/saas/mgt/api/common/operation/new"
                payload = {"businessId":sub['id'],"type":10150014,"createAt":"","id":"","userId":self.__userId}
                self.__session.post(url, data=json.dumps(payload))
                url = f"https://manage.71dj.com/saas/mgt/api/common/operation/delete/user/{self.__userId}?type=10150014&businessId={sub['id']}"
                payload = {}
                self.__session.post(url, data=json.dumps(payload))
            url = "https://manage.71dj.com/saas/mgt/api/common/operation/new"
            payload = {"userId":self.__userId,"businessId":item['id'],"unitId":"","type":"10150016"}
            self.__session.post(url, data=json.dumps(payload))
            url = f"https://manage.71dj.com/saas/mgt/api/common/operation/delete/user/{self.__userId}?type=10150016&userId={self.__userId}&businessId={item['id']}"
            self.__result = self.__session.post(url, data=json.dumps(payload)).json()['msg']

    def __article(self):
        """
        文章收藏
        :return:
        """
        url = "https://manage.71dj.com/saas/mgt/api/document/recommend/list?category=&page=1&pageSize=2"
        self.__session.headers = {"Content-Type": "application/json;charset=utf-8", "Authorization": "bearer " + self.__access_token}
        self.__result = self.__session.get(url).json()['result']['records']
        for item in self.__result:
            url = "https://manage.71dj.com/saas/mgt/api/common/operation/new"
            payload = {"businessId":item['id'],"type":10150018,"createAt":"","id":"","userId":self.__userId}
            self.__result = self.__session.post(url, data=json.dumps(payload)).json()['result']
            url = f"https://manage.71dj.com/saas/mgt/api/common/operation/delete/user/{self.__userId}?type=10150018&businessId={item['id']}"
            self.__result = self.__session.post(url, data=json.dumps(payload)).json()['msg']

    def __unknown(self):
        """
        不记得是啥了
        :return:
        """
        url = "https://manage.71dj.com/saas/mgt/api/study/study-content/pageApp?pageSize=2&page=1"
        self.__session.headers = {"Content-Type": "application/json;charset=utf-8", "Authorization": "bearer " + self.__access_token}
        payload = {"topicType": 211101}
        self.__result = self.__session.post(url, data=json.dumps(payload)).json()['result']['records']
        for item in self.__result:
            url = "https://manage.71dj.com/saas/mgt/api/common/comment/new"
            payload = {"unitId":self.__unitId,"userId":self.__userId,"businessType":item['topicId'],"body":"已学习","commentImages":[],"businessId":item['id']}
            self.__result = self.__session.post(url, data=json.dumps(payload)).json()['result']
            url = "https://manage.71dj.com/saas/mgt/api/common/comment/delete/" + self.__result
            payload = {}
            self.__result = self.__session.post(url, data=json.dumps(payload)).json()['msg']



    def run(self):
        print("--started--")
        self.__host()
        print("调用接口:", self.__hosted)
        self.__encrypt()
        print("加密密码:", self.__encrypted)
        self.__login()
        print("登陆凭证:", self.__access_token)
        self.__sign()
        print("签到结果:", self.__result)
        self.__app()
        print("生活服务:", self.__result)
        self.__red()
        print("红色土地:", self.__result)
        self.__faq()
        print("问答模块:", self.__result)
        self.__article()
        print("文章收藏:", self.__result)
        self.__unknown()
        print("未知项目:", self.__result)
        print("--finished--")


if __name__ == '__main__':

    SIGN("手机号", "密码").run()
