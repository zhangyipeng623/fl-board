from peewee import *
import datetime


db = MySQLDatabase(
    "fl", user="fl", host="192.168.3.106", password="password", charset="utf8mb4"
)


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


def init_table():
    # 更新表
    db.create_tables([User, Node])


if __name__ == "__main__":
    init_table()
