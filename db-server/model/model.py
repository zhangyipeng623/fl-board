from peewee import *
from config import config

db = MySQLDatabase(
    config.Mysql_db,
    user=config.Mysql_user,
    host=config.Mysql_host,
    password=config.Mysql_password,
    charset="utf8mb4",
    connect_timeout=10,
)
import datetime


class BaseModel(Model):
    class Meta:
        database = db


class Node(BaseModel):
    id = AutoField()
    node_name = CharField(null=False)
    ip = CharField(null=False)
    port = IntegerField(null=False)
    system = CharField(null=False)
    cpu = CharField(null=False)
    gpu = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "node"


class User(BaseModel):
    id = AutoField()
    username = CharField(unique=True)
    password = CharField(null=False)
    node = ForeignKeyField(
        Node, field=Node.id, backref="users", null=False
    )  # 修改字段名和参数
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "users"


class DataBase(BaseModel):
    id = AutoField()
    db_name = CharField(null=False)
    user_id = IntegerField(null=False)
    username = CharField(null=False)
    field = TextField(null=False)
    data_number = IntegerField(null=False, default=0)
    file_name = CharField(null=False)
    detail = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "data_base"


class Ruler(BaseModel):
    id = AutoField()
    ruler_name = CharField(null=False)
    ruler_field = TextField(null=False)
    aligned_db = TextField(null=False)
    original_db = TextField(null=False)
    data_count = IntegerField(null=False)
    file_name = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "ruler"


class RulerDetail(BaseModel):
    id = AutoField()
    ruler_id = IntegerField(null=False)
    original_node = TextField(null=False)
    operator = TextField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "ruler_detail"


class Net(BaseModel):
    id = AutoField()
    net_name = CharField(null=False)
    node_name = CharField(null=False)
    input_num = IntegerField(null=False)
    output_num = IntegerField(null=False)
    file_name = CharField(null=False)
    detail = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "net"


class Job(BaseModel):
    id = AutoField()
    job_id = CharField(null=False)
    node_name = CharField(null=False)
    db_id = IntegerField(null=False)
    db_name = CharField(null=False)
    net_name = CharField(null=False)
    net_id = IntegerField(null=False)
    input_field = CharField(null=False)
    output_field = CharField(null=False)
    status = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "job"
