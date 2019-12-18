import hashlib
import time

from user.weiboapi import OAuthWeibo
from wtoken.views import make_token

import jwt
from django.http import JsonResponse
from django.shortcuts import render
import json
from .models import UserProfile
from tools.logging_check import logging_check

# Create your views here.
@logging_check('PUT')
def users(request,username=None):

    if request.method == 'GET':
        if username:
            users = UserProfile.objects.filter(username=username)
            user = users[0]
            # TODO 没用户 返回提示
            # 拿具体用户数据
            # 有查询字符串[?nickname=1] or 没查询字符串
            if request.GET.keys():
                # 查询字符串
                data = {}
                for k in request.GET.keys():
                    if hasattr(user,k):
                        # 过滤字段
                        if k == 'password':
                            continue
                        v = getattr(user,k)
                        data[k] = v
                res = {'code':200,'username':username,'data':data}


            else:
                # 无查询字符串
                users = UserProfile.objects.filter(username=username)
                user = users[0]
                res = {'code':200,'username':username,'data':{'nickname':user.nickname,'sign':user.sign,
                                                              'info':user.info,'avatar':str(user.avatar)}}

            return JsonResponse(res)

        else:
            # 拿数据
            all_users = UserProfile.objects.all()
            users_data = []
            for user in all_users:
                dic = {}
                dic['nickname'] = user.nickname
                dic['username'] = user.username
                dic['sign'] = user.sign
                dic['info'] = user.info
                users_data.append(dic)
            res = {'code':200,'data':users_data}
            return JsonResponse(res)


    elif request.method == 'POST':
        # 创建用户
        json_str = request.body
        if not json_str:
            result = {'code':10102,'error':'Please give me data~'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        username = json_obj.get('username')
        email = json_obj.get('email')
        if not username:
            result = {'code':10101,'error':'Please give me username~'}
            return JsonResponse(result)
        # TODO 检查 json dict 中的key 是否存在
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        if password_1 != password_2:
            result = {'code':10103,'error':'The password is error!'}
            return JsonResponse(result)
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code':10104,'error':'The username is already existed!'}
            return JsonResponse(result)

        # 生成散列的密码
        pm = hashlib.md5()
        pm.update(password_1.encode())

        # 创建用户
        try:
            UserProfile.objects.create(username=username,password=pm.hexdigest(),nickname=username,email=email)
        except Exception as e:
            print('---create error---')
            print(e)
            result = {'code':10105,'error':'The username is already existed!!'}
            return JsonResponse(result)

        # 生成token
        token = make_token(username,3600*24)
        result = {'code':200,'data':{'token':token.decode()},'usernmae':username}
        return JsonResponse(result)


    elif request.method == 'PUT':
        # 更新 http://127.0.0.1:8000/v1/users/username
        if not username:
            res = {'code':10108,'error':'Must be give me username!!'}
            return JsonResponse(res)
        json_str = request.body
        # TODO 空Body判断
        json_obj = json.loads(json_str)
        nickname = json_obj.get('nickname')
        sign = json_obj.get('sign')
        info = json_obj.get('info')
        # 更新
        # users = UserProfile.objects.filter(username=username)
        # user = users[0]
        user = request.user
        # 当前请求,token用户 修改自己的数据
        if user.username != nickname:
            result = {'code':10109,'error':'The username is error!'}
            return JsonResponse(result)

        to_update = False
        if user.nickname != nickname:
            to_update = True
        if user.info != info:
            to_update = True
        if user.sign != sign:
            to_update = True

        if to_update:
            # 做更新
            user.sign = sign
            user.nickname = nickname
            user.info = info
            user.save()
        return JsonResponse({'code':200,'username':username})


@logging_check('POST')
def users_avatar(request,username):
    # 处理头像上传
    if request.method != 'POST':
        result = {'code':10110,'error':'Please user POST'}
        return JsonResponse(result)
    user = request.user
    if user.username != username:
        result = {'code':10109,'error':'The username is error!'}
        return JsonResponse(result)
    user.avatar = request.FILES['avatar']
    user.save()
    return JsonResponse({'code':200,'username':username})


def users_weibo_url(request):

    oauth = OAuthWeibo('123')
    oauth_weibo_url = oauth.get_weibo_login()
    return JsonResponse({'code':200,'oauth_url':oauth_weibo_url})


# http://127.0.0.1:5000/login_callback?state=123&code=d3e4e90cb4e3d89ce0379c5a44175509