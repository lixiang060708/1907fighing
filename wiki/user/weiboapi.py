 # -*- coding:utf-8 -*-
import requests
from urllib.parse import urlencode
from django.conf import settings


class OAuthWeibo(object):

    def __init__(self, state=None, scope=None):
        # 网站应用客户端id
        self.client_id = settings.WEIBO_CLIENT_ID
        # 网站应用客户端安全密钥
        self.client_secret = settings.WEIBO_CLIENT_SECRET
        # 网站回调url网址
        self.redirect_uri = settings.REDIRECT_URI
        # 防止csrf
        self.state = state
        # 授权范围
        self.scope = scope

    def get_weibo_login(self):
        """
        用于获取微博登陆的URL
        :return: 微博登陆的网址
        """
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
        }
        if self.scope:
            params['scope'] = self.scope

        # 拼接url地址
        weibo_url = 'https://api.weibo.com/oauth2/authorize?'
        # url = 'client_id=123050457758183&redirect_uri=http://www.example.com/response&response_type=code'
        url = weibo_url + urlencode(params)
        return url

    def get_access_token_uid(self, code):
        weibo_token_url = 'https://api.weibo.com/oauth2/access_token?'
        req_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        print('#######')
        print(req_data)
        try:
            response = requests.post(weibo_token_url, data=req_data)
        except Exception:
            raise Exception('获取access_token异常')
        if response.status_code == 200:
            return response.text
        print(response.text)
        raise Exception('获取access_token异常')
