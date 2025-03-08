"""
数据对齐规则模块

该模块提供了数据对齐规则相关的API接口，包括添加规则、获取规则列表、获取规则详情等功能。
主要用于处理不同数据源之间的数据对齐操作。
"""

from typing import List, Union
import uuid
import json
import requests
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from model import DataBase, RulerDetail, Node
from model import Ruler as RulerModel
from config import config


ruler = APIRouter(prefix="/ruler")


class DB(BaseModel):
    id: int
    name: str
    nodename: str


class OriginalField(BaseModel):
    field: str
    file_name: str
    node_id: int
    nodename: str


class AlignedField(BaseModel):
    field: str
    type: str


class Operator(BaseModel):
    db: DB
    aligned_field: AlignedField
    operator: str
    original_field: Union[OriginalField, List[OriginalField]]


class Ruler(BaseModel):
    db: DB
    operator: List[Operator]


class RulerInfo(BaseModel):
    ruler_name: str
    aligned_db: str
    original_db: List[DB]
    field: List[AlignedField]
    ruler: List[Ruler]


class UpdateFieldType(BaseModel):
    id: int
    field: str
    type: str


@ruler.post("/add")
def add(ruler_info: RulerInfo) -> dict:
    """
    添加数据对齐规则

    Args:
        ruler_info (RulerInfo): 规则信息，包含规则名称、对齐数据库、原始数据库、字段和规则列表

    Returns:
        dict: 包含状态信息的字典，成功返回 {"status": "success"}

    Raises:
        HTTPException: 当规则为空或创建规则失败时抛出400错误
    """

    file_name = str(uuid.uuid4())
    original_db = ruler_info.original_db
    ruler_model = RulerModel(
        aligned_db=ruler_info.aligned_db,
        ruler_name=ruler_info.ruler_name,
        ruler_field=[field.model_dump()
                     for field in ruler_info.field],  # 序列化字段列表
        original_db=[db.model_dump() for db in original_db],  # 序列化数据库列表
        data_count=0,
        file_name=file_name,
    )
    data_count = 0
    ruler_detail = []
    for ruler_item in ruler_info.ruler:
        data_base = ruler_item.db
        db_item = DataBase.select().where(DataBase.nodename == data_base.nodename,
                                          DataBase.db_name == data_base.name, DataBase.id == data_base.id).get()

        node = db_item.node
        res = requests.post(
            f"http://{node.ip}:{node.port}/aligned/add"
            f"?file_name={file_name}&original_file={db_item.file_name}",
            headers={
                "x-forwarded-for": config.Host
            },
            json=ruler_item.model_dump(),
            timeout=300  # 设置300秒超时，防止请求无限等待
        )
        if res.status_code != 200:
            raise HTTPException(
                400, detail=f"对齐数据失败,res:{res.json().get('detail')}"
            )
        data_count += res.json().get("data_count", 0)

        ruler_detail.append(
            RulerDetail(
                ruler_id=ruler_model.id,
                original_db=ruler_item.db.model_dump(),
                operator=[op.model_dump() for op in ruler_item.operator],
            )
        )
    # try:
    ruler_model.data_count = int(data_count)
    ruler_model.save()
    for detail in ruler_detail:
        detail.ruler_id = ruler_model.id
        detail.save()

    return {"status": "success"}


@ruler.get("/get")
def get(operator: Operator):
    op = operator.operator
    node_id = operator.original_field.node_id
    node = Node.select().where(Node.id == node_id).get()
    res = requests.get(
        f"http://{node.ip}:{node.port}/aligned/get_data",
        headers={
            "x-forwarded-for": config.Host,
        },
        json=operator.model_dump(),
        timeout=300  # 设置300秒超时，防止请求无限等待
    )
    if res.status_code == 200:
        return res.json()
    else:
        raise HTTPException(400, detail=f"获取{op}({operator.original_field})失败")


@ruler.get("/list")
def get_ruler_list():
    ruler_list = RulerModel.select().order_by(RulerModel.updated_at.desc()).dicts()
    ruler_list = list(ruler_list)

    return {"ruler_list": ruler_list}


@ruler.get("/detail")
def get_ruler_detail(request: Request):
    data = json.loads(request.query_params.get("data"))
    ruler_detail = (
        RulerDetail.select()
        .where(
            RulerDetail.ruler_id == data.get(
                "ruler_id"), RulerDetail.original_db == json.loads(data.get("original_db"))
        )
        .get()
    )
    return {
        "original_db": ruler_detail.original_db,
        "operator": ruler_detail.operator,
    }


@ruler.get("/aligned")
def get_aligned_data(request: Request):
    aligned_data = RulerModel.select().order_by(
        RulerModel.updated_at.desc()).dicts()
    aligned_data = list(aligned_data)
    return {"aligned_data": aligned_data}


@ruler.post("/update-field-type")
def update_field_type(field_type: UpdateFieldType):
    ruler_item = RulerModel.select().where(
        RulerModel.id == field_type.id).get_or_none()
    if ruler_item is None:
        raise HTTPException(400, detail="对齐规则不存在")
    original_db_list = ruler_item.original_db
    for original_db in original_db_list:
        db_item = DataBase.select().where(
            DataBase.id == original_db.get("id")).get_or_none()
        if db_item is None:
            raise HTTPException(
                400, detail=f"{original_db.get('name')},数据库不存在")
        node = db_item.node
        json_data = dict(field_type)
        json_data["file_name"] = ruler_item.file_name
        res = requests.post(
            f"http://{node.ip}:{node.port}/aligned/update_field_type",
            json=json_data,
            timeout=300,
            headers={
                "x-forwarded-for": config.Host
            },
        )
        if res.status_code == 200:
            result = res.json()
            if not result.get("convertible", False):
                raise HTTPException(
                    400, detail=result.get("message", "格式无法转换"))
        else:
            raise HTTPException(
                400, detail=res.json().get("detail", "更新字段类型失败"))
    try:
        for field in ruler_item.ruler_field:
            if field["field"] == field_type.field:
                field["type"] = field_type.type
        ruler_item.save()
    except Exception as e:
        raise HTTPException(500, detail=f"更新字段类型失败,{e}") from e
    return {"status": "success"}
