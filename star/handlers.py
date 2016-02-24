# coding=utf-8


from base.requestHandler import *
from base.model import Star, News, Comment


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

        feed_type = int(self.get_argument('type', -1))

        star_id = self.get_argument('star_id', None)

        last_id = self.get_argument('last_id', None)

        offset_date = ModelHelper.get_offset_date(News, last_id)

        parms = dict()

        parms['create_date__lt'] = offset_date

        star_dic_list = []

        if star_id:
            star = Star.objects(id=star_id).first()

            parms['id__in'] = star.news

            star_dic = star.to_mongo()
            star_dic.pop('news')
            star_dic.pop('fans')
            star_dic['fans_count'] = len(star.fans)

            star_dic_list.append({star.id: star_dic})

        else:
            stars = AccountHelper.get_user_by_token(token).following_stars
            stars = Star.objects(id__in=stars)

            news = []

            for star in stars:
                news.extend(star.news)

                star_dic = star.to_mongo()
                star_dic.pop('news')
                star_dic.pop('fans')
                star_dic['fans_count'] = len(star.fans)

                star_dic_list.append({star.id: star_dic})

            parms['id__in'] = news

        if feed_type in FeedType.Types:
            parms['type'] = feed_type

        query_set = News.objects(**parms).order_by('-create_date').limit(15)
        news_list = []

        for news in query_set:

            star_dic = star_dic_list[news.star_id]

            news_dic = news.to_mongo()
            news_dic.pop('star_id')
            news['star'] = star_dic

            news.read_count += 1
            news.save()

            news_list.append(news_dic)

        return self.common_response(SUCCESS_CODE, "获取新闻成功", news_list)


class CommentHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        token = self.get_argument('token')

        AccountHelper.verify_token(token)

        user_id = AccountHelper.get_user_by_token(token).id

        news_id = self.get_argument('news_id')

        content = self.get_argument('content')

        news = News.objects(id=news_id).first()

        if not news:
            return self.common_response(FAILURE_CODE, "评论的新闻不存在")

        news.comment_count += 1
        news.save()

        comment = Comment()
        comment.user_id = user_id
        comment.news_id = news_id
        comment.create_date = datetime.today()
        comment.content = content
        comment.save()

        return self.common_response(SUCCESS_CODE, "评论成功")

    def get(self, *args, **kwargs):
        # 无需鉴权
        news_id = self.get_argument('news_id')

        last_id = self.get_argument('last_id', None)

        offset_date = ModelHelper.get_offset_date(Comment, last_id)

        parms = dict()

        parms['create_date__lt'] = offset_date
        parms['news_id'] = news_id

        query_set = Comment.objects(**parms).order_by('-create_date').limit(15)

        comments = []

        for comment in query_set:
            comments.append(comment.to_mongo())

        return self.common_response(SUCCESS_CODE, "获取评论成功", comments)

    def delete(self, *args, **kwargs):
        token = self.get_argument('token')

        AccountHelper.verify_token(token)

        comment_id = self.get_argument('comment_id')

        comment = Comment.objects(id=comment_id).first()

        if not comment:
            return self.common_response(FAILURE_CODE, "评论不存在")

        news = News.objects(id=comment.news_id).first()
        news.comment_count -= 1
        news.save()

        comment.delete()

        return self.common_response(SUCCESS_CODE, "评论删除成功")
