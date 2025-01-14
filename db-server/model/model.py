from peewee import *
from config import config

db = MySQLDatabase(config.Mysql_db, 
                    user=config.Mysql_user,
                    host=config.Mysql_host, 
                    password=config.Mysql_password,
                    charset='utf8mb4',
                    connect_timeout=10,)
import datetime


class BaseModel(Model):
    class Meta:
        database = db  


class User(BaseModel):
    id = AutoField()
    username = CharField(unique=True)
    password = CharField(null=False)
    ip = CharField(null=False)
    port = IntegerField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'users'  

class DataBase(BaseModel):
    id = AutoField()
    db_name = CharField(null=False)
    user_id = IntegerField(null=False)
    username = CharField(null=False)
    field = TextField(null=False)
    data_number = IntegerField(null=False, default=0)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'data_base'