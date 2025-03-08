"""
数据库模型模块

该模块定义了系统中使用的所有数据库模型类，包括:
- 节点信息
- 用户信息 
- 数据库信息
- 规则信息
- 规则详情
- 网络模型
- 任务信息

使用peewee ORM框架实现数据库操作。
"""

import json
import datetime
from peewee import (
    Model,
    AutoField,
    CharField,
    IntegerField,
    TextField,
    DateTimeField,
    ForeignKeyField,
    MySQLDatabase
)
from config import config

db = MySQLDatabase(
    config.Mysql_db,
    user=config.Mysql_user,
    host=config.Mysql_host,
    password=config.Mysql_password,
    charset="utf8mb4",
    connect_timeout=10,
)


class JSONField(TextField):
    """
    自定义JSON字段类型,用于在数据库中存储JSON格式数据
    继承自TextField,实现了JSON数据和Python对象之间的转换
    """

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


class BaseModel(Model):
    """
    基础模型类

    所有数据库模型的基类，提供数据库连接配置。
    继承自peewee.Model,为所有子模型提供统一的数据库连接。
    继承:
        Model: peewee ORM的基础模型类
    """
    class Meta:
        database = db


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


class User(BaseModel):
    id = AutoField()
    username = CharField(unique=True)
    password = CharField(null=False)
    node = ForeignKeyField(
        column_name='node_id', model=Node, field=Node.id, backref="users", null=False
    )
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "users"


class DataBase(BaseModel):
    id = AutoField()
    db_name = CharField(null=False)
    node = ForeignKeyField(column_name='node_id', model=Node,
                           field=Node.id, backref="users", null=False)
    nodename = CharField(null=False)
    field = JSONField(null=False)
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
    ruler_field = JSONField(null=False)
    aligned_db = TextField(null=False)
    original_db = JSONField(null=False)
    data_count = IntegerField(null=False)
    file_name = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "ruler"


class RulerDetail(BaseModel):
    id = AutoField()
    ruler_id = IntegerField(null=False)
    original_db = JSONField(null=False)
    operator = JSONField(null=False)
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
