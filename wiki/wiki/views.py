from django.http import JsonResponse
from user.models import UserProfile
import redis

def test(request):

    r = redis.Redis(host='127.0.0.1',port=6379,db=0)
    while True:
        try:
            with r.lock('guoxiaonao',blocking_timeout=3) as lock:
            # 对score字段进行+1操作
                u = UserProfile.objects.get(username='guoxiaonao')
                u.score += 1
                u.save()
            break
        except Exception as e:
            print('Lock failed')


    return JsonResponse({'code':200,'data':{}})