# coding=utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

import re

from base.requestHandler import *

define("port", default=8000, help="Run on 8000", type=int)


class SmscodeHandler(BaseRequestHandler):

    def post(self, *args, **kwargs):
        username = self.get_argument('username')

        if re.match(TEL_PATTERN, username):
            if not self.smscode_expired_or_not_exist(username):
                return self.write(self.common_response(FAILURE_CODE, "短信验证码未过期!"))

            smscode = self.get_smscode()
            self.redis.set(username + SMSCODE_SUFFIX, smscode, ex=60 * 5)
            self.write(self.common_response(SUCCESS_CODE, "验证码获取成功", smscode=smscode))

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

        if Tools.has_registered(username):
            return self.write(self.common_response(FAILURE_CODE, "该手机号码已经注册!"))

        if not inner_smscode or inner_smscode != smscode:
            return self.write(self.common_response(FAILURE_CODE, "短信验证码输入错误或已经过期!"))

        if not re.match(PASSWORD_PATTERN, password):
            return self.write(self.common_response(FAILURE_CODE, "非法的密码模式!"))

        password = Tools.md5(password)

        user = User(username=username,
                    password=password)
        user.save()

        token = Tools.generate_token(username)

        self.write(self.common_response(SUCCESS_CODE, "注册成功!", token=token))


class LoginHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')

        user = User.objects(username=username).first()

        if not user:
            return self.write(self.common_response(FAILURE_CODE, "该用户不存在!"))

        if not user.password == password:
            return self.write(self.common_response(FAILURE_CODE, "密码错误!"))

        token = Tools.generate_token(username)

        self.write(self.common_response(SUCCESS_CODE, "登录成功!", token=token))


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


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/smscode", SmscodeHandler),
                                            (r"/register", RegisterHandler),
                                            (r"/login", LoginHandler),
                                            (r"/forget", ForgetHandler),
                                            (r"/password", PasswordHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()