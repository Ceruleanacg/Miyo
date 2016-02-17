# coding=utf-8

from mongoengine import *

connect(host="mongodb://Shuyu:Wangshuyu1993@localhost/fanidols")


class User(Document):
    username = StringField()
    password = StringField()
    nick_name = StringField()

    # sex : 0男, 1女
    sex = IntField(0, 1, default=0)
    age = IntField(default=0)

    province_id = IntField(default=0)

    following_stars = ListField()


class Province(Document):
    ProID = IntField()
    ProSort = IntField()
    name = StringField()
    ProRemark = StringField()


class Post(Document):
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

    source = StringField()

    # type : zixun咨询, woshouhui握手会, ...
    type = StringField()

    title = StringField()

    article = StringField()

    read_count = IntField()

    image_urls = ListField()

    comments = ListField()

    stars = ListField(required=True)

    create_date = DateTimeField()


class Star(Document):
    name = StringField(required=True)

    avatar_url = StringField()

    news = ListField()
    feed = ListField()

    fans = ListField()
