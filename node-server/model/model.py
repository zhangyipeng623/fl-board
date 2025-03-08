# from peewee import *
# from config import config
# import datetime
# import csv

# db = MySQLDatabase(
#     config.Mysql_db,
#     user=config.Mysql_user,
#     host=config.Mysql_host,
#     password=config.Mysql_password,
#     charset="utf8mb4",
#     connect_timeout=10,
# )


# def insert_data_from_csv(file_path, table_name, column_names=None):
#     with open(file_path, "r") as file:
#         reader = csv.reader(file)
#         if column_names is None:
#             column_names = next(reader)
#         else:
#             column_names = column_names
#         model_class = type(
#             table_name,
#             (BaseModel,),
#             {name: CharField() for name in column_names + ["created_at"]},
#         )
#         db.create_tables([model_class], safe=True)
#         data_count = 0
#         for row in reader:
#             if row == column_names:
#                 continue
#             data = dict(zip(column_names, row))
#             data["created_at"] = datetime.datetime.now()
#             model_class.create(**data)
#             data_count += 1
#         db.close()
#         return data_count


# class BaseModel(Model):
#     class Meta:
#         database = db


# class User(BaseModel):
#     id = AutoField()
#     username = CharField(unique=True)
#     password = CharField(null=False)
#     ip = CharField(null=False)
#     port = IntegerField(null=False)
#     created_at = DateTimeField(default=datetime.datetime.now)
#     updated_at = DateTimeField(default=datetime.datetime.now)

#     class Meta:
#         table_name = "users"
