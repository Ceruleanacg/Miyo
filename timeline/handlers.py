# coding=utf-8

import re

from base.requestHandler import *
from base.model import Feed


class TimelineHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        token = self.get_argument('token')
        Tools.verify_token(token)

        # 等待关注系统完成