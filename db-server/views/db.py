"""数据库操作相关的路由模块

本模块提供了数据库操作的各种API端点，包括:
- 数据库信息的上传
- 数据库列表的获取
- 数据库字段的查询
等功能
"""
import json
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from model import DataBase, User, redis
from pydantic import BaseModel

db = APIRouter(prefix="/db")


class DBInfo(BaseModel):
    user_id: int
    db_name: str
    field: dict
    detail: str
    data_count: int
    file_name: str


@db.get("/original")
def get_original_list():
    database = DataBase.select().order_by(DataBase.updated_at.desc())
    db_list = list(database.dicts())

    return {"db_list": db_list}


@db.post("/upload")
def upload(request: Request, db_info: DBInfo):
    session = request.headers.get("Authorization")
    if session is None:
        raise HTTPException(401, detail="请先登录")
    user_info = redis.get(session)
    user_info = json.loads(user_info)
    if user_info["id"] != db_info.user_id:
        raise HTTPException(401, detail="数据不正确")
    user = User.get_or_none(User.id == db_info.user_id)
    if user is None:
        raise HTTPException(401, detail="用户不存在")
    else:
        try:
            field = db_info.field
            if (
                DataBase.select()
                .where(
                    DataBase.db_name == db_info.db_name,
                    DataBase.nodename == user.node.nodename,
                )
                .exists()
            ):
                raise HTTPException(400, detail="数据库已存在")
            DataBase.create(
                user_id=user_info["id"],
                db_name=db_info.db_name,
                field=field,
                node=user.node,
                detail=db_info.detail,
                file_name=db_info.file_name,
                data_number=db_info.data_count,
                nodename=user.node.nodename,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            return {"message": "数据上传成功"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"数据上传失败,err:{e}") from e


@db.get("/list")
def get_db_list(request: Request):
    db_list = (
        DataBase.select(
            DataBase.db_name.alias("label"),
            DataBase.id.alias("value"),
            DataBase.nodename,
        )
        .where(DataBase.node == request.query_params.get("node_id"))
        .order_by(DataBase.updated_at.desc())
        .dicts()
    )

    db_list = list(db_list)
    for db_item in db_list:
        db_item["value"] = json.dumps(
            {
                "id": db_item["value"],
                "name": db_item["label"],
                "nodename": db_item["nodename"],
            }
        )
    return {"db_list": db_list}


@db.get("/field")
def get_filed(request: Request):
    db_param = str(request.query_params.get("db"))
    db_item = json.loads(db_param)
    data_base = (
        DataBase.select()
        .where(
            DataBase.db_name == db_item["name"],
            DataBase.nodename == db_item["nodename"],
            DataBase.id == db_item["id"],
        )
        .get()
    )
    field = data_base.field
    field_list = []
    for key in field:
        field_list.append(
            {
                "label": f"{key}: {field[key]}",
                "value": json.dumps(
                    {
                        "field": key,
                        "file_name": data_base.file_name,
                        "node_id": data_base.node.id,
                        "nodename": f"{data_base.nodename}-{data_base.db_name}",
                    }
                ),
            }
        )
    return {"field_list": field_list}
