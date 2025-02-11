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


class Net(BaseModel):
    id = AutoField()
    net_name = CharField(null=False)
    node_name = CharField(null=False)
    input_num = IntegerField(null=False)
    output_num = IntegerField(null=False)
    file_name = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'net'

def init_table():
    # 更新表
    db.create_tables([Net])


if __name__ == '__main__':
    init_table()