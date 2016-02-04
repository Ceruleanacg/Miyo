# coding=utf-8

import hashlib
import time

from base.config import *
from base.model import User

class Tools(object):

    # redis 引用自 config.py
    redis = Redis

    @classmethod
    def get_user_by_token(cls, token):
        object_id = cls.redis.hget(token + TOKEN_SUFFFIX, OBJECT_ID_KEY)
        user = User.objects(id=object_id).first()
        return user

    @classmethod
    def has_registered(cls, username):
        user = User.objects(username=username).first()
        return True if user else False

    @classmethod
    def generate_token(cls, username):
        timestamp = time.time()
        return Tools.md5(username + str(timestamp))

    @classmethod
    def md5(cls, raw_str):
        m = hashlib.md5()
        m.update(raw_str)
        return m.hexdigest()
