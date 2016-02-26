# coding=utf-8

import tornado.web

import redis

import hashlib
import random
import time
import math
import os
import re

import numpy

from PIL import Image
from sklearn import svm
from sklearn.externals import joblib

from json import JSONEncoder
from datetime import datetime
from mongoengine.fields import ObjectId

from base.config import *
from base.model import User


Redis = redis.Redis(host='localhost', port=6379, db=0)

base_dir = os.path.dirname(__file__)


class ModelHelper(object):
    @classmethod
    def get_offset_date(cls, model, last_id):

        offset_date = datetime.today()

        if last_id:
            last_model = model.objects(id=last_id).first()

            if last_model:
                offset_date = last_model.create_date

        return offset_date

    @classmethod
    def generate_comment_dic(cls, comment):
        user = User.objects(id=comment.user_id).first()

        user_dic = user.to_mongo()
        user_dic.pop('username')
        user_dic.pop('password')

        comment_dic = comment.to_mongo()
        comment_dic.pop('user_id')
        comment_dic.pop('news_id')
        comment_dic['user'] = user_dic

        return comment_dic


class AccountHelper(object):

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
        return cls._generate_token_if_need(username)

    @classmethod
    def _generate_token_if_need(cls, username):
        user = User.objects(username=username).first()
        token = cls.get_token_by_user(user)

        if not token:
            timestamp = time.time()
            token = Tools.md5(username + str(timestamp))

            cls.redis.set(str(user.id) + ID_TO_TOKEN_SUFFIX, token, ex=60 * 60 * 24 * 7)
            cls.redis.set(token + TOKEN_TO_ID_SUFFIX, user.id, ex=60 * 60 * 24 * 7)

        return token


class Tools(object):

    @classmethod
    def md5(cls, raw_str):
        m = hashlib.md5()
        m.update(raw_str)
        return m.hexdigest().upper()


class CaptchaHacker(object):

    classifier_path = os.path.join(base_dir, 'captchas/classifier/classifier.pkl')

    pois = []

    recognizer = joblib.load(classifier_path)

    @classmethod
    def recognize(cls, poi_images):
        captchas = ""
        for poi_image in poi_images:
            captchas += cls.recognizer.predict(poi_image).tolist().pop()
        return captchas

    @classmethod
    def slice(cls, image, need_save=False):

        mat_image = numpy.array(image)

        gray_image = cls.filter_color(mat_image)

        binary_image = numpy.where(numpy.logical_or(gray_image < 30, gray_image > 225), numpy.uint8(255), numpy.uint8(0))

        binary_image = 255 - binary_image

        col_sums = binary_image.sum(axis=0)

        cls._get_poi(gray_image, col_sums, 0)

        pil_image = Image.fromarray(gray_image)

        images = []

        for poi in cls.pois:
            poi_image = pil_image.crop(poi)

            if not cls.check_if_poi_image_legal(poi_image):
                continue

            poi_image = poi_image.resize((12, 20))

            if need_save:
                path = os.path.join(base_dir, 'captchas', 'split', Tools.md5(str(random.random())) + '.jpg')
                poi_image.save(path, 'jpeg')
            else:
                images.append(numpy.array(poi_image).reshape(1, -1))

        cls.pois = []

        return images

    @classmethod
    def filter_color(cls, image):

        rgb_image = image.copy()

        for row in xrange(rgb_image.shape[0]):
            for col in xrange(rgb_image.shape[1]):
                rgb_vec = rgb_image[row, col]

                target_distance = math.sqrt(rgb_vec[0] ** 2 + rgb_vec[1] ** 2 + rgb_vec[2] ** 2)

                if target_distance >= 255:
                    rgb_image[row, col] = [255, 255, 255]

        gray_image = Image.fromarray(rgb_image).convert('L')

        return numpy.array(gray_image)

    @classmethod
    def check_if_poi_image_legal(cls, image):
        return False if image.size[0] < 10 or image.size[0] > 35 or image.size[1] < 10 else True

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
                            # 当前列为0, 检查后第2列是否也为0, 以及是否越界

                            if _col + 2 < width - 1:
                                if col_sums[_col + 2] == 0:
                                    boundary_flag = True
                                else:
                                    # 该列后第2列不为0, 有效信息中间0为字符丢失信息
                                    continue
                            else:
                                # 该列后第2列越界, 将此列作为右边界
                                boundary_flag = True

                            if boundary_flag:
                                # 该列后第2列也为0, 该列是右边界
                                left_col = col
                                right_col = _col

                                top_y = cls._get_top_y(image, left_col, right_col)
                                bottom_y = cls._get_bottom_y(image, left_col, right_col)

                                left_x = left_col
                                right_x = right_col

                                poi = (left_x, top_y, right_x, bottom_y)

                                if abs(top_y - bottom_y) > 4:
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
    def split_captchas(cls):

        captchas_dir = './captchas/full'

        filenames = os.listdir(captchas_dir)

        for filename in filenames:
            captchas_path = os.path.join(captchas_dir, filename)
            cls.slice(numpy.array(Image.open(captchas_path)))

    @classmethod
    def mark_feature(cls):
        captchas_dir = './captchas/split'
        train_dir = './captchas/train'

        filenames = os.listdir(captchas_dir)

        for filename in filenames:

            if filename.find('jpg') < 0:
                continue

            captchas_path = os.path.join(captchas_dir, filename)

            image = Image.open(captchas_path)
            image.show()

            save_flag = True

            while True:
                result = raw_input()

                if re.match("^(\w)$", result):
                    save_flag = True
                    break
                else:
                    if result == 'esc':
                        save_flag = False
                        break

            if save_flag:
                if not os.path.exists(os.path.join(train_dir, result)):
                    os.mkdir(os.path.join(train_dir, result))
                image.save(os.path.join(train_dir, result, filename))

    @classmethod
    def train(cls):
        train_dir = './captchas/train'

        images = []
        targets = []

        for target_name in os.listdir(train_dir):
            if len(target_name) == 1:
                for filename in os.listdir(os.path.join(train_dir, target_name)):
                    if filename.find('jpg') > 0:

                        image = numpy.array(Image.open(os.path.join(train_dir, target_name, filename)))

                        targets.append(target_name)
                        images.append(image)

        images = numpy.array(images)

        data = images.reshape(images.shape[0], -1)
        targets = numpy.array(targets)

        classifier = svm.SVC(kernel='poly', degree=3)
        classifier.fit(data, targets)

        joblib.dump(classifier, cls.classifier_path, compress=3)


class JsonEncoder(JSONEncoder):
    def default(self, obj, **kwargs):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return JSONEncoder.default(obj, **kwargs)
