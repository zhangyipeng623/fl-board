from peewee import *
import datetime


db = MySQLDatabase("fl", 
                    "root",
                    "localhost", 
                    "password",
                    charset='utf8mb4')

class BaseModel(Model):
    class Meta:
        database = db  


class User(BaseModel):
    id = AutoField()
    username = CharField(unique=True)
    password = CharField()
    ip = CharField(null=False)
    port = IntegerField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'users' 
def init_table():
    db.create_tables([User])

if __name__ == '__main__':
    init_table()