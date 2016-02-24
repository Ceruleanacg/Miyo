# coding=utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from account.handlers import *

define("port", default=8000, type=int)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/v1/account/smscode", SmscodeHandler),
                                            (r"/v1/account/register", RegisterHandler),
                                            (r"/v1/account/login", LoginHandler),
                                            (r"/v1/account/forget", ForgetHandler),
                                            (r"/v1/account/password", PasswordHandler),
                                            (r"/v1/account/info", InfoHandler),
                                            (r"/v1/account/province", ProvinceHandler)])

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
