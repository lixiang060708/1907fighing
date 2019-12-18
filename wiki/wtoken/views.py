import hashlib
import time

import jwt
from django.shortcuts import render
from django.http import JsonResponse
import json
from user.models import UserProfile

# Create your views here.
def tokens(request):
    # 登录页面
    if request.method != 'POST':
        result = {'code':20101,'error':'Please use POST'}
        return JsonResponse(result)
    json_str = request.body
    #TODO 检查参数是否存在
    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    password = json_obj.get('password')
    # 找用户
    users = UserProfile.objects.filter(username=username)
    if not users:
        result = {'code':20102,'error':'The username or password is error!'}
        return JsonResponse(result)
    user = users[0]
    pm = hashlib.md5()
    pm.update(password.encode())
    if user.password != pm.hexdigest():
        result = {'code':20103,'error':'The username or password is error!!'}
        return JsonResponse(result)

    # 生成token
    token = make_token(username,3600*24)
    result = {'code':200,'username':username,'data':{'token':token.decode()}}
    return JsonResponse(result)


def make_token(username,exp):
    # 生成token
    key = '1234567ab'
    now_t = time.time()
    payload = {'username':username,'exp':int(now_t+exp)}
    return jwt.encode(payload,key,algorithm='HS256')