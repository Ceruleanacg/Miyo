# coding=utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import sys

from account.handlers import *

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/v1/account/smscode", SmscodeHandler),
                                            (r"/v1/account/register", RegisterHandler),
                                            (r"/v1/account/login", LoginHandler),
                                            (r"/v1/account/forget", ForgetHandler),
                                            (r"/v1/account/password", PasswordHandler),
                                            (r"/v1/account/info", InfoHandler),
                                            (r"/v1/account/province", ProvinceHandler),
                                            (r"/v1/account/favo", FavoriteHandler)])

    port = sys.argv[1]

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
