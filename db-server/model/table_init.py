from peewee import *
import datetime


db = MySQLDatabase("fl", 
                    user="root",
                    host="10.211.55.12", 
                    password="password",
                    charset='utf8mb4')

class BaseModel(Model):
    class Meta:
        database = db  


class Ruler(BaseModel):
    id = AutoField()
    ruler_name = CharField(null=False)
    ruler_field = TextField(null=False)
    original_db = TextField(null=False)
    data_count = IntegerField(null=False)
    file_name = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'ruler'

def init_table():
    # 更新表
    db.create_tables([ Ruler])


if __name__ == '__main__':
    init_table()