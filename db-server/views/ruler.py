from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Union
from model import DataBase, User, RulerDetail
from model import Ruler as RulerModel
import requests, uuid, json


ruler = APIRouter(prefix="/ruler")


class Operator(BaseModel):
    db_name_id: str
    field_name_id: str
    operator: str
    field_value: Union[str, List[str]]


class Ruler(BaseModel):
    name_id: str
    operator: List[Operator]


class RulerInfo(BaseModel):
    ruler_name: str
    aligned_db: str
    original_db: List[str]
    field: str
    ruler: List[Ruler]


@ruler.post("/add")
def add(ruler_info: RulerInfo):
    ruler_list = ruler_info.ruler
    file_name = uuid.uuid4()
    original_db = ""
    for db in ruler_info.original_db:
        original_db += f"{db},"
    original_db = original_db[:-1]
    ruler_model = RulerModel(
        aligned_db=ruler_info.aligned_db,
        ruler_name=ruler_info.ruler_name,
        ruler_field=ruler_info.field,
        original_db=original_db,
        data_count=0,
        file_name=file_name,
    )
    data_count = 0
    ruler_detail = []
    for ruler in ruler_list:
        name, username = ruler.name_id.split("-")
        node = (
            DataBase.select()
            .where(DataBase.username == username, DataBase.db_name == name)
            .get()
        )
        user = (
            User.select()
            .where(User.username == username, User.id == node.user_id)
            .get()
        )
        res = requests.post(
            f"http://{user.ip}:{user.port}/aligned/add?file_name={file_name}&original_file={node.file_name}",
            json=ruler.model_dump(),
        )
        if res.status_code != 200:
            raise HTTPException(
                400, detail=f"对齐数据失败，res:{res.json().get('detail')}"
            )
        data_count += res.json().get("data_count", 0)
        op = []
        for operator in ruler.operator:
            op.append(operator.model_dump())

        ruler_detail.append(
            RulerDetail(
                ruler_id=ruler_model.id,
                original_node=ruler.name_id,
                operator=json.dumps(op),
            )
        )
    # try:
    ruler_model.data_count = data_count
    ruler_model.save()
    for detail in ruler_detail:
        detail.ruler_id = ruler_model.id
        detail.save()
    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=f"创建规则失败，res:{e}")
    return {"status": "success"}


@ruler.get("/get")
def get(operator: Operator):
    op = operator.operator
    field, userid, file_name = operator.field_value.split(",")
    user = User.select().where(User.id == userid).get()
    res = requests.get(
        f"http://{user.ip}:{user.port}/aligned/get_data?op={op}&field={field}&file_name={file_name}"
    )
    if res.status_code == 200:
        return res.json()
    else:
        raise HTTPException(400, detail=f"获取{op}({field})失败")


@ruler.get("/list")
def get_ruler_list():
    ruler_list = RulerModel.select().order_by(RulerModel.updated_at.desc()).dicts()
    ruler_list = list(ruler_list)

    return {"ruler_list": ruler_list}


@ruler.get("/detail")
def get_ruler_detail(request: Request):
    ruler_id = request.query_params.get("ruler_id")
    original_node = request.query_params.get("original_node")
    ruler_detail = (
        RulerDetail.select()
        .where(
            RulerDetail.ruler_id == ruler_id, RulerDetail.original_node == original_node
        )
        .get()
    )
    operator = json.loads(ruler_detail.operator)
    return json.dumps(
        {"ruler_detail": {"original_node": original_node, "operator": operator}}
    )


@ruler.get("/aligned")
def get_aligned_data(request: Request):
    aligned_data = RulerModel.select().order_by(RulerModel.updated_at.desc()).dicts()
    aligned_data = list(aligned_data)
    return {"aligned_data": aligned_data}
