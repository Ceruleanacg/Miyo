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
    app = tornado.web.Application(handlers=[(r"/account/smscode", SmscodeHandler),
                                            (r"/account/register", RegisterHandler),
                                            (r"/account/login", LoginHandler),
                                            (r"/account/forget", ForgetHandler),
                                            (r"/account/password", PasswordHandler),
                                            (r"/account/info", InfoHandler),
                                            (r"/account/province", ProvinceHandler)])

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
