from config import *

class User(Document):
    username = StringField(required=True)
    password = StringField(required=True)
