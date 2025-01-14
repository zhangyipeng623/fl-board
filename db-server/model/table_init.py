from peewee import *
import datetime


db = MySQLDatabase("fl", 
                    user="root",
                    host="localhost", 
                    password="password",
                    charset='utf8mb4')

class BaseModel(Model):
    class Meta:
        database = db  


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

def init_table():
    db.create_tables([DataBase])

if __name__ == '__main__':
    init_table()