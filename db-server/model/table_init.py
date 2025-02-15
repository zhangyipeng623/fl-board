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


class Job(BaseModel):
    id=AutoField()
    job_id = CharField(null=False)
    node_name = CharField(null=False)
    net_name = CharField(null=False)
    net_id = IntegerField(null=False)
    input_field = CharField(null=False)
    output_field = CharField(null=False)
    status = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = 'job'

def init_table():
    # 更新表
    db.create_tables([Job])


if __name__ == '__main__':
    init_table()