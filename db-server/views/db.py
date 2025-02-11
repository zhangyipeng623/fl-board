from fastapi import APIRouter,Request,HTTPException
from model import DataBase
from model import redis
import json
from datetime import datetime
from pydantic import BaseModel

db = APIRouter(prefix="/db")

class DBInfo(BaseModel):
    user_id: int
    db_name: str
    field: str
    data_count: int
    file_name: str
@db.get("/original")
def original():
    database = DataBase.select().order_by(DataBase.updated_at.desc())
    db_list = list(database.dicts())

    return {"db_list": db_list}

@db.post("/upload")
def upload(request: Request,db_info: DBInfo):
    session = request.query_params.get("session")
    user_info = redis.get(session)
    user_info = json.loads(user_info)
    if user_info["id"] != db_info.user_id:
        raise HTTPException(status_code=401, detail="数据不正确")
    else:
        try:
            fields = json.loads(db_info.field)
            field = ""
            for f in fields:
                field += f + ","
            field = field[:-1]
            DataBase.create(user_id=user_info["id"], 
                                db_name=db_info.db_name, 
                                field=field, 
                                file_name=db_info.file_name,
                                data_number=db_info.data_count,
                                username=user_info["username"],
                                created_at=datetime.now(),
                                updated_at=datetime.now()
                                )
            return {"message": "数据上传成功"}
        except:
            raise HTTPException(status_code=500, detail="数据上传失败")
        
@db.get("/list")
def get_list(request: Request):
    db_list = DataBase.select(DataBase.db_name.alias("label"), DataBase.id.alias("value"),DataBase.username).where(DataBase.user_id == request.query_params.get("node_id")).order_by(DataBase.updated_at.desc()).dicts()
    db_list = list(db_list)
    for db in db_list:
        db["value"] = f"{db['label']}-{db['username']}"
    return {"db_list": db_list}

@db.get("/field")
def get_filed(request: Request):
    name_id = request.query_params.get("name_id")
    name_id = name_id.split("-")
    db_name = name_id[0]
    user_name = name_id[1]
    field = DataBase.select(DataBase.field, DataBase.file_name,DataBase.user_id).where(DataBase.db_name == db_name, DataBase.username == user_name).get()
    # ["field0", "field1", "field2", "field3", "field4"]
    file_name = field.file_name
    userid = field.user_id
    fields = field.field.split(",")
    field_list = []
    for f in fields:
        field_list.append({"label": f, "value": f + "," + str(userid) + "," + file_name})
    return {"field_list": field_list}