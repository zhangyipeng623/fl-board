from fastapi import APIRouter, Request, HTTPException
import requests
from pydantic import BaseModel
from typing import Union, List, Optional
import os, csv
from utils.utils import add, sub, mul, div
from config import config

aligned = APIRouter(prefix="/aligned")


class Operator(BaseModel):
    db_name_id: str
    field_name_id: str
    operator: str
    field_value: Union[str, List[str], float, int]
    data: Optional[Union[str, float, int]] = None


class Ruler(BaseModel):
    name_id: str
    operator: List[Operator]


@aligned.get("/get_data")
def get_data(request: Request):
    op = request.query_params.get("op")
    field = request.query_params.get("field")
    file_name = request.query_params.get("file_name")
    with open(f"data/original/{file_name}.csv", "r") as file:
        reader = csv.DictReader(file)
        if op == "avg":
            values = [float(row[field]) for row in reader]
            return round(sum(values) / len(values), 2)
        elif op == "max":
            values = [float(row[field]) for row in reader]
            return round(max(values), 2)
        elif op == "min":
            values = [float(row[field]) for row in reader]
            return round(min(values), 2)


@aligned.post("/add")
def add_aligned(ruler: Ruler, request: Request):
    file_name = request.query_params.get("file_name")
    original_file = request.query_params.get("original_file")
    datacount = 0
    # 读取原始文件
    with open(f"data/original/{original_file}.csv", "r") as original_file_f, open(
        f"data/aligned/{file_name}.csv", "w"
    ) as aligned_file_f:
        original_file = csv.DictReader(original_file_f)
        # 读取标题
        title = []
        for r in ruler.operator:
            if r.operator == "avg" or r.operator == "max" or r.operator == "min":
                res = requests.get(
                    f"http://{config.center_host}:{config.center_port}/ruler/get",
                    json=r.model_dump(),
                )
                if res.status_code != 200:
                    raise HTTPException(401, detail=f"{res.json().get('detail')}")
                else:
                    r.data = res.json()
            elif (
                r.operator == "+"
                or r.operator == "-"
                or r.operator == "*"
                or r.operator == "/"
                or r.operator == "="
            ):
                pass
            title.append(r.field_name_id)
        aligned_file = csv.DictWriter(aligned_file_f, fieldnames=title)
        aligned_file.writeheader()
        # 读取数据
        for row in original_file:
            datacount += 1
            aligned_row = {title: None for title in aligned_file.fieldnames}
            for r in ruler.operator:
                if r.operator == "avg" or r.operator == "max" or r.operator == "min":
                    aligned_row[r.field_name_id] = r.data
                elif (
                    r.operator == "+"
                    or r.operator == "-"
                    or r.operator == "*"
                    or r.operator == "/"
                ):
                    try:
                        data = []
                        for f in r.field_value:
                            filed = f.split(",")[0]
                            data.append(round(float(row[filed]), 2))
                        if r.operator == "+":
                            aligned_row[r.field_name_id] = add(*data)
                        elif r.operator == "-":
                            aligned_row[r.field_name_id] = sub(*data)
                        elif r.operator == "*":
                            aligned_row[r.field_name_id] = mul(*data)
                        elif r.operator == "/":
                            aligned_row[r.field_name_id] = div(*data)
                    except Exception as e:
                        raise HTTPException(401, detail=f"{e}")
                elif r.operator == "=":
                    filed = r.field_value.split(",")[0]
                    aligned_row[r.field_name_id] = row[filed]
            aligned_file.writerow(aligned_row)

    return {"message": "aligned", "data_count": datacount}
