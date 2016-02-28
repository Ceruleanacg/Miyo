# coding=utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from star.handlers import *

define("port", default=8000, type=int)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/v1/star/follow", FollowHandler),
                                            (r"/v1/star/news", NewsHandler),
                                            (r"/v1/star/news/comment", CommentHandler),
                                            (r"/v1/star/stars", StarsHandler)])

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
