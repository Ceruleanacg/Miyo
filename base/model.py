# coding=utf-8

from mongoengine import *

connect(host="mongodb://Shuyu:Wangshuyu1993@localhost/fanidols")


class User(Document):
    username = StringField(required=True)
    password = StringField(required=True)
    nick_name = StringField(required=True)

    sex = IntField(0, 1, default=0, required=True)
    age = IntField(default=0, required=True)

    province_id = IntField(default=0, required=True)



