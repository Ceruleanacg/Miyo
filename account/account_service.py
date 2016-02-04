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
    app = tornado.web.Application(handlers=[(r"/smscode", SmscodeHandler),
                                            (r"/register", RegisterHandler),
                                            (r"/login", LoginHandler),
                                            (r"/forget", ForgetHandler),
                                            (r"/password", PasswordHandler),
                                            (r"/info", InfoHandler),
                                            (r"/province", ProvinceHandler)])

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
