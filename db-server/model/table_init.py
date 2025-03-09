from peewee import *
import datetime
import json


db = MySQLDatabase(
    "fl", user="root", host="10.211.55.12", password="password", charset="utf8mb4"
)


class BaseModel(Model):
    class Meta:
        database = db


class JSONField(TextField):
    def db_value(self, value):
        """将Python对象转换为数据库存储格式"""
        if value is None:
            return None
        return json.dumps(value)

    def python_value(self, value):
        """将数据库数据转换为Python对象"""
        if value is None:
            return None
        return json.loads(value)


class Node(BaseModel):
    id = AutoField()
    nodename = CharField(null=False)
    ip = CharField(null=False)
    port = IntegerField(null=False)
    system = CharField(null=False)
    cpu = CharField(null=False)
    gpu = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "node"


class Job(BaseModel):
    id = AutoField()
    Job_id = CharField(null=False)
    node_name = CharField(null=False)
    db_id = IntegerField(null=False)
    db_name = CharField(null=False)
    net_name = CharField(null=False)
    net_id = IntegerField(null=False)
    input_field = JSONField(null=False)
    output_field = JSONField(null=False)
    status = CharField(null=False)
    total = IntegerField(null=False)
    finished = IntegerField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "job"


class NodeJob(BaseModel):
    id = AutoField()
    node = ForeignKeyField(column_name='node_id', model=Node,
                           field=Node.id, backref="jobs", null=False)
    job_id = CharField(null=False)
    status = CharField(null=False)
    total = IntegerField(null=False)
    finished = IntegerField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "node_job"


def init_table():
    # 更新表
    db.create_tables([Job, NodeJob])


if __name__ == "__main__":
    init_table()
