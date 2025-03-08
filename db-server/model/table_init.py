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
    original_node = JSONField(null=False)
    operator = JSONField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "ruler_detail"



def init_table():
    # 更新表
    db.create_tables([Ruler,RulerDetail])


if __name__ == "__main__":
    init_table()
