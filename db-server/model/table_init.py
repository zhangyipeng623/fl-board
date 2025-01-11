from .model import *


def init_table():
    db.create_tables([User])
