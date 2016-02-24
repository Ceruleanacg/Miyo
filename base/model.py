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


class News(Document):
    url = StringField()

    source = StringField()

    # type : 0: 新闻, 1: 其他
    type = IntField()

    title = StringField()

    article = StringField()

    read_count = IntField()

    comment_count = IntField()

    image_urls = ListField()

    star_id = ObjectIdField()

    create_date = DateTimeField()

    meta = {
        'indexes': ['create_date']
    }


class Star(Document):
    name = StringField(required=True)

    avatar_url = StringField()

    weibo_url = StringField()

    news = ListField()
    fans = ListField()

    meta = {
        'indexes': ['name']
    }



class Comment(Document):
    user_id = ObjectIdField()
    news_id = ObjectIdField()

    create_date = DateTimeField()

    content = StringField()

    meta = {
        'indexes': ['create_date']
    }
