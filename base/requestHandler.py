# coding=utf-8

import tornado.web

import json

from tools.tools import *


class BaseRequestHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseRequestHandler, self).__init__(application, request, **kwargs)
        self.set_header("Content-Type", "application/json")
        self.redis = Redis

    _ARG_DEFAULT = []

    def get_argument(self, name, default=_ARG_DEFAULT, strip=True):
        if self.request.method == "GET":
            return super(BaseRequestHandler, self).get_argument(name, default, strip)
        else:
            try:
                return json.loads(self.request.body)[name]
            except KeyError or ValueError:
                raise tornado.web.HTTPError(400)

    def common_response(self, code, msg, results=None):
        if not results:
            results = dict()

        return self.write(json.dumps(dict(code=code,
                                          msg=msg,
                                          results=results),
                                     cls=JsonEncoder))
