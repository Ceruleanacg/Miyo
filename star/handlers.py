# coding=utf-8

import re
import datetime

from base.requestHandler import *
from base.model import User, Star, News


class FollowHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):

        token = self.get_argument('token')

        AccountHelper.verify_token(token)

        user = AccountHelper.get_user_by_token(token)

        star_id = self.get_argument('star_id')

        if ObjectId(star_id) in user.following_stars:
            return self.common_response(FAILURE_CODE, "已经关注该明星")

        star = Star.objects(id=star_id).first()

        if not star:
            return self.common_response(FAILURE_CODE, "该明星不存在")

        star.fans.append(user.id)
        star.save()

        user.following_stars.append(star.id)
        user.save()

        return self.common_response(SUCCESS_CODE, "关注成功")

    def delete(self, *args, **kwargs):
        token = self.get_argument('token')

        AccountHelper.verify_token(token)

        star_id = self.get_argument('star_id')

        user = AccountHelper.get_user_by_token(token)

        if ObjectId(star_id) not in user.following_stars:
            return self.common_response(FAILURE_CODE, "没有关注该明星")

        star = Star.objects(id=star_id).first()

        if not star:
            return self.common_response(FAILURE_CODE, "该明星不存在")

        star.fans.remove(user.id)
        star.save()

        user.following_stars.remove(star.id)
        user.save()

        return self.common_response(SUCCESS_CODE, "取消关注成功")


class NewsHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        token = self.get_argument('token')

        AccountHelper.verify_token(token)

        feed_type = int(self.get_argument('type'))

        last_news_id = self.get_argument('last_id', None)

        last_news = News.objects(id=last_news_id).first() if last_news_id else None

        offset_date = last_news.create_date if last_news else datetime.today()

        if feed_type == FeedType.All:

            query_set = News.objects(create_date__lt=offset_date).order_by('-create_date').limit(15)
            news_list = []

            for news in query_set:
                news_list.append(news.to_mongo())

        elif feed_type == FeedType.News or feed_type == FeedType.Post:

            query_set = News.objects(type=feed_type, create_date__lt=offset_date).order_by('-create_date').limit(15)
            news_list = []

            for news in query_set:
                news_list.append(news.to_mongo())

            return self.common_response(SUCCESS_CODE, "获取新闻成功", news_list)

        else:
            return self.common_response(FAILURE_CODE, "未知Feed数据类型")

