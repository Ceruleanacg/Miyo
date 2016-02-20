# coding=utf-8

TEL_PATTERN = "0?(13|14|15|17|18)[0-9]{9}"
PASSWORD_PATTERN = "^[\w]{6,18}$"
NICK_NAME_PATTERN = "^[\w]{4,18}$"
YEAR_PATTERN = "201(\d)"
MONTH_PATTERN = "(\d){2}"

SUCCESS_CODE = 0
FAILURE_CODE = -1

SMSCODE_SUFFIX = "_SMSCODE"

TOKEN_TO_ID_SUFFIX = "_TOKEN_TO_ID"
ID_TO_TOKEN_SUFFIX = "_ID_TO_TOKEN"

HOST = 'localhost'

DB_NAME = "fanidols"


class FeedType(object):
    News = 0
    Post = 1

    Types = [News, Post]
