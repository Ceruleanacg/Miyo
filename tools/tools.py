# coding=utf-8

import tornado.web

import redis

import hashlib
import time

import numpy

from PIL import Image
from scipy.ndimage import morphology

from json import JSONEncoder
from mongoengine.fields import ObjectId

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
    def verify_token(cls, token):
        if not cls.redis.get(token + TOKEN_TO_ID_SUFFIX):
            raise tornado.web.HTTPError(401)

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


class CaptchaHacker(object):

    pois = []

    @classmethod
    def recognize(cls, image):
        pass

    @classmethod
    def slice(cls, image):
        ero_image = cls.pretreat(image)

        col_sums = ero_image.sum(axis=0)

        cls._get_poi(ero_image, col_sums, 0)

        pil_image = Image.fromarray(ero_image)

        for poi in cls.pois:
            pil_image.crop(poi).show()

        cls.pois = []

    @classmethod
    def _get_poi(cls, image, col_sums, start_col):
        if start_col >= image.shape[1]:
            return
        else:
            width = image.shape[1]

            for col in range(start_col, width):
                if col_sums[col] > 0:
                    for _col in range(col, width):
                        if col_sums[_col] > 0:
                            continue
                        else:
                            # 当前列为0, 检查后第3列是否也为0, 以及是否越界

                            if _col + 3 < width - 1:
                                if col_sums[_col + 3] == 0:
                                    boundary_flag = True
                                else:
                                    # 该列后第三列不为0, 有效信息中间0为字符丢失信息
                                    continue
                            else:
                                # 该列后第三列越界, 将此列作为右边界
                                boundary_flag = True

                            if boundary_flag:
                                # 该列后第三列也为0, 该列是右边界
                                left_col = col
                                right_col = _col

                                top_y = cls._get_top_y(image, left_col, right_col)
                                bottom_y = cls._get_bottom_y(image, left_col, right_col)

                                poi = (left_col, top_y, right_col, bottom_y)

                                print poi

                                cls.pois.append(poi)

                                return cls._get_poi(image, col_sums, right_col + 1)
                else:
                    continue

    @classmethod
    def _get_top_y(cls, image, start_col, end_col):

        height = image.shape[0]

        for row in xrange(height):
            for col in range(start_col, end_col + 1):
                if image[row, col] > 0:
                    return row

    @classmethod
    def _get_bottom_y(cls, image, start_col, end_col):

        height = image.shape[0]

        for row in xrange(height):
            for col in range(start_col, end_col + 1):
                if image[-1 - row, col] > 0:
                    return height - row - 1

    @classmethod
    def pretreat(cls, image):
        image = numpy.where(numpy.logical_or(image < 4, image > 165), 255, image)
        ero_image = morphology.grey_erosion(image, size=(1, 1))
        ero_image = 255 - ero_image
        return ero_image


class JsonEncoder(JSONEncoder):
    def default(self, obj, **kwargs):
        if isinstance(obj, ObjectId):
            return str(obj)
        else:
            return JSONEncoder.default(obj, **kwargs)


if __name__ == '__main__':
    CaptchaHacker.slice(numpy.array(Image.open('show.png').convert('L')))