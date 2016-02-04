# coding=utf-8

import re

from base.requestHandler import *


class TimelineHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        token = self.get_argument('token')
        Tools.verify_token(token)

        pass