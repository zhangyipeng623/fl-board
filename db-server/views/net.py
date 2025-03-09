from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from model import Net, redis, User
from fastapi import UploadFile, File, Form, Request
import ast
import uuid
import json
from ast import ClassDef
from typing import List

net = APIRouter(prefix="/net")


def check_code_elements(code: str, target_classes: List[str] = None, target_functions: List[str] = None) -> dict:
    """检查代码中是否包含目标类和函数

    Args:
        code: 源代码字符串
        target_classes: 要检查的类名列表
        target_functions: 要检查的函数名列表

    Returns:
        dict: 包含找到的类和函数的字典
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"classes": [], "functions": []}

    found_classes = []
    found_functions = []

    for node in ast.walk(tree):
        if target_classes and isinstance(node, ast.ClassDef) and node.name in target_classes:
            found_classes.append(node.name)
        elif target_functions and isinstance(node, ast.FunctionDef) and node.name in target_functions:
            found_functions.append(node.name)

    return {
        "classes": found_classes,
        "functions": found_functions
    }


@net.get("/list")
def get_net_list():
    # 获得网络模型列表
    database = Net.select().order_by(Net.updated_at.desc())
    net_list = list(database.dicts())

    return {"net_list": net_list}


@net.post("/upload")
async def net_upload(
    request: Request,
    file: UploadFile = File(...),
    netName: str = Form(),
    inputNum: int = Form(),
    outputNum: int = Form(),
    detail: str = Form(),
    user_id: int = Form(),
):
    session = request.headers.get("Authorization")
    user_info = redis.get(session)
    user_info = json.loads(user_info)
    if user_info["id"] != user_id:
        raise HTTPException(401, detail="数据不正确")
    user = User.get_or_none(User.id == user_id)
    if not user:
        raise HTTPException(401, detail="用户不存在")
    # 上传网络模型
    if not file.filename.endswith(".py"):
        raise HTTPException(400, "仅支持 Python 文件 (.py)")
    try:
        # 读取文件内容
        contents = await file.read()
        code = contents.decode("utf-8")
    except Exception as e:
        raise HTTPException(400, "文件解码失败，请确保是有效的 UTF-8 文本文件") from e

    found_elements = check_code_elements(
        code, ["Net"], ["transform_x", "transform_y", "get_optimizer", "get_criterion"])
    print(found_elements)
    if ("Net" not in found_elements["classes"] or
        "transform_x" not in found_elements["functions"] or
            "transform_y" not in found_elements["functions"] or
            "get_optimizer" not in found_elements["functions"] or
            "get_criterion" not in found_elements["functions"]):
        raise HTTPException(
            400, "文件内容中未找到 Net 类 或 transform_x、transform_y、get_optimizer、get_criterion函数")
    file_name = uuid.uuid4()

    # 保存文件
    with open(f"./data/net/{file_name}.py", "wb") as f:
        f.write(contents)
    try:
        Net.create(
            net_name=netName,
            nodename=user.node.nodename,
            file_name=file_name,
            input_num=inputNum,
            output_num=outputNum,
            detail=detail,
            node_id=user.node.id,
        )
    except Exception as e:
        raise HTTPException(400, f"上传失败，res:{e}") from e
    return {"status": "success"}


@net.get("/detail")
async def get_net_detail(request: Request):
    net_id = request.query_params.get("net_id")
    net = Net.select().where(Net.id == net_id).get()
    file_name = net.file_name
    with open(f"./data/net/{file_name}.py", "r") as f:
        code = f.read()
    return {"code": code}


@net.get("/get_net_file")
def get_net_file(request: Request):
    file_name = request.query_params.get("net_id")

    # 文件完整路径
    file_path = f"./data/net/{file_name}.py"
    try:
        return FileResponse(
            path=file_path,  # 文件路径
            media_type="application/octet-stream",  # 文件的内容类型，可随需求调整
            filename=f"{file_name}.py",  # 下载的文件名，例如：net_id.py
        )

    except FileNotFoundError:
        raise HTTPException(404, detail="文件未找到")
