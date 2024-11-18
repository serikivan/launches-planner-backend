import redis
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings


# Connect to our Redis instance
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def getUserBySession(request):
    session_id = request.COOKIES.get('session_id')
    if session_id:
        try:
            username = session_storage.get(session_id).decode('utf-8')
            print(username)
            user = get_user_model().objects.get(email = username)
        except AttributeError:
            user = AnonymousUser()
    else:
        user = AnonymousUser()
    return user