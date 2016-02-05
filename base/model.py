# coding=utf-8

from mongoengine import *

connect(host="mongodb://Shuyu:Wangshuyu1993@localhost/fanidols")


class User(Document):
    username = StringField(required=True)
    password = StringField(required=True)
    nick_name = StringField()

    # sex : 0男, 1女
    sex = IntField(0, 1, default=0)
    age = IntField(default=0)

    province_id = IntField(default=0)


class Province(Document):
    ProID = IntField()
    ProSort = IntField()
    name = StringField()
    ProRemark = StringField()


class Feed(Document):
    avatar_url = StringField()
    name = StringField()

    # type : 0新闻, 1动态
    type = IntField()

    # source_type : 0官网, 1微博, 2推特, 3ins
    source_type = IntField()

    create_date = DateTimeField()

    head_line = StringField()
    head_image_url = StringField()

    content_url = StringField()


class News(Document):
    url = StringField()

    # type : zixun咨询, woshouhui握手会
    type = StringField()

    title = StringField()
    article = StringField()
    image_urls = ListField()