import redis

from mongoengine import *

TEL_PATTERN = "0?(13|14|15|17|18)[0-9]{9}"
PASSWORD_PATTERN = "^[\w]{6,18}$"

SUCCESS_CODE = 0
FAILURE_CODE = -1

USERNAME_KEY = "username"
OBJECT_ID_KEY = "object_ID"

SMSCODE_SUFFIX = "_SMSCODE"
TOKEN_SUFFFIX = "_TOKEN"

HOST = '58.96.191.210'

DB_NAME = "fanidols"

connect(host="mongodb://Shuyu:Wangshuyu1993@58.96.191.210/fanidols")

Redis = redis.Redis(host='58.96.191.210', port=6379, db=0)
