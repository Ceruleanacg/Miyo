# coding=utf-8

import re

from base.requestHandler import *

from base.model import Province


class SmscodeHandler(BaseRequestHandler):

    def post(self, *args, **kwargs):
        username = self.get_argument('username')

        if re.match(TEL_PATTERN, username):
            if not self.smscode_expired_or_not_exist(username):
                return self.write(self.common_response(FAILURE_CODE, "短信验证码未过期!"))

            smscode = self.get_smscode()
            self.redis.set(username + SMSCODE_SUFFIX, smscode, ex=60 * 5)
            self.write(self.common_response(SUCCESS_CODE, "验证码获取成功", dict(smscode=smscode)))

        else:
            self.write(self.common_response(FAILURE_CODE, "用户名非法!"))

    def smscode_expired_or_not_exist(self, username):
        return False if self.redis.ttl(username + SMSCODE_SUFFIX) > 0 else True

    def get_smscode(self):
        return "0000"


class RegisterHandler(BaseRequestHandler):

    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')
        smscode = self.get_argument('smscode')

        # 只有在 注册 与 密码重置 与 密码修改 时, 密码使用明文传输

        inner_smscode = self.redis.get(username + SMSCODE_SUFFIX)

        if AccountHelper.has_registered(username):
            return self.write(self.common_response(FAILURE_CODE, "该手机号码已经注册!"))

        if not inner_smscode or inner_smscode != smscode:
            return self.write(self.common_response(FAILURE_CODE, "短信验证码输入错误或已经过期!"))

        if not re.match(PASSWORD_PATTERN, password):
            return self.write(self.common_response(FAILURE_CODE, "非法的密码模式!"))

        password = Tools.md5(password)

        user = User(username=username,
                    password=password)
        user.save()

        token = AccountHelper.generate_token(username)

        self.write(self.common_response(SUCCESS_CODE, "注册成功!", dict(token=token)))


class LoginHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')

        user = User.objects(username=username).first()

        if not user:
            return self.write(self.common_response(FAILURE_CODE, "该用户不存在!"))

        if not user.password == password:
            return self.write(self.common_response(FAILURE_CODE, "密码错误!"))

        token = AccountHelper.generate_token(username)

        self.write(self.common_response(SUCCESS_CODE, "登录成功!", dict(token=token)))


class ForgetHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')
        smscode = self.get_argument('smscode')

        # 只有在 注册 与 密码重置 与 密码修改 时, 密码使用明文传输

        user = User.objects(username=username).first()

        if not user:
            return self.write(self.common_response(FAILURE_CODE, "该用户不存在!"))

        inner_smscode = self.redis.get(username + SMSCODE_SUFFIX)

        if not inner_smscode or inner_smscode != smscode:
            return self.write(self.common_response(FAILURE_CODE, "短信验证码输入错误或已经过期!"))

        if not re.match(PASSWORD_PATTERN, password):
            return self.write(self.common_response(FAILURE_CODE, "非法的密码模式!"))

        password = Tools.md5(password)

        if password == user.password:
            return self.write(self.common_response(FAILURE_CODE, "重置密码不可与原密码相同!"))

        user.password = password
        user.save()

        self.write(self.common_response(SUCCESS_CODE, "密码重置成功!"))


class PasswordHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        old_password = self.get_argument('old_password')
        new_password = self.get_argument('new_password')

        if old_password == new_password:
            return self.write(self.common_response(FAILURE_CODE, "新旧密码不可相同!"))

        if not re.match(PASSWORD_PATTERN, new_password):
            return self.write(self.common_response(FAILURE_CODE, "新密码模式非法!"))

        user = User.objects(username=username).first()

        if not user:
            return self.write(self.common_response(FAILURE_CODE, "用户不存在!"))

        user.password = Tools.md5(new_password)
        user.save()

        self.write(self.common_response(SUCCESS_CODE, "密码修改成功!"))


class InfoHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        token = self.get_argument('token')
        AccountHelper.verify_token(token)

        nick_name = self.get_argument('nick_name')
        sex = self.get_argument('sex')
        age = self.get_argument('age')
        province_id = self.get_argument('province_id')

        if not re.match(NICK_NAME_PATTERN, nick_name):
            return self.write(self.common_response(FAILURE_CODE, "昵称为4~18位字符!"))

        if not isinstance(sex, int) or sex > 1 or sex < 0:
            return self.write(self.common_response(FAILURE_CODE, "性别不合法!"))

        if age > 150 or age < 0:
            return self.write(self.common_response(FAILURE_CODE, "年龄不合法!"))

        if province_id > 34 or province_id < 0:
            return self.write(self.common_response(FAILURE_CODE, "地区不合法!"))

        user = AccountHelper.get_user_by_token(token)
        user.nick_name = nick_name
        user.sex = sex
        user.age = age
        user.province_id = province_id
        user.save()

        self.write(self.common_response(SUCCESS_CODE, "信息修改成功!"))

    def get(self, *args, **kwargs):
        token = self.get_argument('token')
        AccountHelper.verify_token(token)

        user = AccountHelper.get_user_by_token(token)

        # 用户有可能被删除, 需要检查是否存在

        user_dic = user.to_mongo()
        user_dic.pop('password')

        if user:
            self.write(self.common_response(SUCCESS_CODE, "用户信息获取成功!", user_dic))
        else:
            self.write(self.common_response(FAILURE_CODE, "用户不存在!"))


class ProvinceHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        token = self.get_argument('token')
        AccountHelper.verify_token(token)

        provinces = Province.objects().all()

        province_list = []

        for pro in provinces:
            province_list.append(pro.to_mongo())

        self.write(self.common_response(SUCCESS_CODE, "省份信息获取成功!", province_list))

