from peewee import *
from model import User


db = MySQLDatabase("fl", 
                    "root",
                    "localhost", 
                    "password",
                    charset='utf8mb4')
def init_table():
    db.create_tables([User])

if __name__ == '__main__':
    init_table()