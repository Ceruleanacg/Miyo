# coding=utf-8

from mongoengine import *

connect(host="mongodb://Shuyu:Wangshuyu1993@localhost/fanidols")


class User(Document):
    username = StringField(required=True)
    password = StringField(required=True)
    nick_name = StringField()

    sex = IntField(0, 1, default=0)
    age = IntField(default=0)

    province_id = IntField(default=0)



