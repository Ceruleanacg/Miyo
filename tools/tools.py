# coding=utf-8

import redis

import hashlib
import time

from base.config import *
from base.model import User

Redis = redis.Redis(host='localhost', port=6379, db=0)


class Tools(object):

    # redis 引用自 config.py
    redis = Redis

    @classmethod
    def get_user_by_token(cls, token):
        object_id = cls.redis.get(token + TOKEN_TO_ID_SUFFIX)
        user = User.objects(id=object_id).first()
        return user

    @classmethod
    def get_token_by_user(cls, user):
        token = cls.redis.get(str(user.id) + ID_TO_TOKEN_SUFFIX)
        return token

    @classmethod
    def has_registered(cls, username):
        user = User.objects(username=username).first()
        return True if user else False

    @classmethod
    def generate_token(cls, username):
        return Tools._generate_token_if_need(username)

    @classmethod
    def _generate_token_if_need(cls, username):
        user = User.objects(username=username).first()
        token = Tools.get_token_by_user(user)

        if not token:
            timestamp = time.time()
            token = Tools.md5(username + str(timestamp))

            cls.redis.set(str(user.id) + ID_TO_TOKEN_SUFFIX, token, ex=60 * 60 * 24 * 7)
            cls.redis.set(token + TOKEN_TO_ID_SUFFIX, user.id, ex=60 * 60 * 24 * 7)

        return token

    @classmethod
    def md5(cls, raw_str):
        m = hashlib.md5()
        m.update(raw_str)
        return m.hexdigest()
