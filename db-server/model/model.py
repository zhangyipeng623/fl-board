from peewee import *
from config import config

db = MySQLDatabase(config.Mysql_db, 
                    user=config.Mysql_user,
                    host=config.Mysql_host, 
                    password=config.Mysql_password,
                    charset='utf8mb4')
import datetime


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

