# coding=utf-8

import re

from base.requestHandler import *
from base.model import User, Star


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
