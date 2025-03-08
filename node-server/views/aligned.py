"""用于处理数据对齐的路由模块"""
from typing import Union, List
import pandas as pd
import requests
import os
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from utils.utils import add, sub, mul, div
from config import config

aligned = APIRouter(prefix="/aligned")


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


class UpdateFieldType(BaseModel):
    id: int
    field: str
    type: str
    file_name: str


def convert_type(value, type_str):
    """根据类型字符串转换数据类型"""
    try:
        if type_str == "int":
            return int(value)
        elif type_str == "float":
            return float(value)
        elif type_str == "str":
            return str(value)
        elif type_str == "list":
            return list(value)
        return value
    except (ValueError, TypeError):
        return value


@aligned.get("/get_data")
def get_data(operator: Operator):
    """
    获取数据对齐结果
    Args:
        request (Request): 请求对象
        operator (Operator): 操作符对象
    Returns:
        dict: 包含状态信息的字典，成功返回 {"status": "success"}
    """
    field = operator.original_field.field
    chunk_size = 10000
    try:
        if operator.operator == "avg":
            count = 0
            total = 0
            for chunk in pd.read_hdf(f"data/original/{operator.original_field.file_name}.h5",
                                     chunksize=chunk_size):
                count += len(chunk)
                total += chunk[field].sum()
            return float(total / count)
        elif operator.operator == "max":
            max_val = float('-inf')
            for chunk in pd.read_hdf(f"data/original/{operator.original_field.file_name}.h5",
                                     chunksize=chunk_size):
                max_val = max(max_val, chunk[field].max())
            return float(max_val)
        elif operator.operator == "min":
            min_val = float('inf')
            for chunk in pd.read_hdf(f"data/original/{operator.original_field.file_name}.h5",
                                     chunksize=chunk_size):
                min_val = min(min_val, chunk[field].min())
            return float(min_val)
    except Exception as e:
        raise HTTPException(401, detail=f"{e}") from e


@aligned.post("/add")
def add_aligned(ruler: Ruler, request: Request):
    file_name = request.query_params.get("file_name")
    original_file = request.query_params.get("original_file")
    other_data = {}
    for r in ruler.operator:
        if r.operator == "avg" or r.operator == "max" or r.operator == "min":
            try:
                # 设置请求超时时间为5秒
                res = requests.get(
                    f"http://{config.center_host}:{config.center_port}/ruler/get",
                    json=r.model_dump(),
                    timeout=5
                )
                if res.status_code != 200:
                    raise HTTPException(
                        401, detail=f"{res.json().get('detail')}")
                else:
                    other_data[f"{r.aligned_field.field}"] = res.json()
            except requests.Timeout as e:
                raise HTTPException(408, detail="Request timeout") from e
            except requests.RequestException as e:
                raise HTTPException(
                    500, detail=f"Request failed: {str(e)}") from e
        elif (
            r.operator == "+"
            or r.operator == "-"
            or r.operator == "*"
            or r.operator == "/"
            or r.operator == "="
        ):
            pass

    # 读取h5文件，使用分块读取
    chunk_size = 10000  # 每次处理10000行数据
    datacount = 0

    # 分块读取和处理数据
    for chunk in pd.read_hdf(f"data/original/{original_file}.h5", chunksize=chunk_size):
        chunk_data = {}

        # 初始化每个字段的数组
        for r in ruler.operator:
            chunk_data[r.aligned_field.field] = []

        # 处理当前块的数据
        for _, row in chunk.iterrows():
            datacount += 1
            for r in ruler.operator:
                if r.operator == "avg" or r.operator == "max" or r.operator == "min":
                    chunk_data[r.aligned_field.field].append(
                        convert_type(
                            other_data[r.aligned_field.field], r.aligned_field.type)
                    )
                elif r.operator in ["+", "-", "*", "/"]:
                    try:
                        data = []
                        for f in r.original_field:
                            filed = f.field
                            data.append(round(float(row[filed]), 2))
                        result = None
                        if r.operator == "+":
                            result = add(*data)
                        elif r.operator == "-":
                            result = sub(*data)
                        elif r.operator == "*":
                            result = mul(*data)
                        elif r.operator == "/":
                            result = div(*data)
                        chunk_data[r.aligned_field.field].append(
                            convert_type(result, r.aligned_field.type)
                        )
                    except Exception as e:
                        raise HTTPException(401, detail=f"{e}") from e
                elif r.operator == "=":
                    filed = r.original_field.field
                    chunk_data[r.aligned_field.field].append(row[filed])

        # 将当前块的数据转换为DataFrame
        chunk_df = pd.DataFrame(chunk_data)
        min_itemsize = {}
        for column in chunk_df.select_dtypes(include=['object']).columns:
            min_itemsize[column] = 100  # 为每个字符串列设置最大长度
        # 分段存储数据，使用append模式
        chunk_df.to_hdf(
            f"data/aligned/{file_name}.h5",
            key='df',
            mode='a',  # 使用append模式
            append=True,  # 启用追加模式
            format='table',  # 使用table格式支持追加
            min_itemsize=min_itemsize  # 为字符串列预分配空间
        )

        # 清理内存
        del chunk_df
        del chunk_data

    # 返回处理结果
    return {"message": "aligned", "data_count": datacount}


@aligned.post("/update_field_type")
def update_field_type(
    field_type: UpdateFieldType
):
    file_path = f"data/aligned/{field_type.file_name}.h5"
    if not os.path.exists(file_path):
        raise HTTPException(401, detail=f"{field_type.file_name}文件不存在")

    chunk_size = 10
    try:
        # 只读取第一个数据块进行检查
        for chunk in pd.read_hdf(file_path, chunksize=chunk_size):
            try:
                # 尝试转换数据类型，但不保存
                _ = chunk[field_type.field].astype(field_type.type)
                return {"message": "字段类型可以转换", "convertible": True}
            except (ValueError, TypeError) as e:
                return {
                    "message": f"字段类型无法转换: {str(e)}",
                    "convertible": False
                }
            break  # 只检查第一个数据块
    except Exception as e:
        print(str(e))
        raise HTTPException(
            status_code=500,
            detail=f"检查字段类型时发生错误: {str(e)}"
        ) from e
