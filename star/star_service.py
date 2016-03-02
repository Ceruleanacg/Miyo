# coding=utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import sys

from star.handlers import *


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/v1/star/follow", FollowHandler),
                                            (r"/v1/star/stars", StarsHandler)])

    port = sys.argv[1]

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
