from fastapi import APIRouter,HTTPException
from model import Net,redis
from fastapi import UploadFile, File, Form,Request
import ast,uuid, json
from ast import ClassDef
from typing import List

net = APIRouter(prefix="/net")


def check_class_in_code(code: str, target_class: List[str]) ->  List[str]:
    """检查代码中是否包含目标类"""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    
    found_class = []
    for node in ast.walk(tree):
        if isinstance(node, ClassDef) and node.name in target_class:
            found_class.append(node.name)
    return found_class

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
    netName:str = Form(),
    inputNum:int = Form(),
    outputNum:int = Form(),
    detail:str = Form(),
    user_id:int = Form(),
    ):
    session = request.query_params.get("session")
    user_info = redis.get(session)
    user_info = json.loads(user_info)
    if user_info["id"] != user_id:
        raise HTTPException(401, detail="数据不正确")

    # 上传网络模型
    if not file.filename.endswith(".py"):
        raise HTTPException(400, "仅支持 Python 文件 (.py)")
    try:
        # 读取文件内容
        contents = await file.read()
        code = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, "文件解码失败，请确保是有效的 UTF-8 文本文件")
    
    found_class = check_class_in_code(code, ["Net","DataSet"])
    if "Net" not in found_class or "DataSet" not in found_class:
        raise HTTPException(400, "文件内容中未找到 Net 或 DataSet 类")
    file_name = uuid.uuid4()
    
    # 保存文件
    with open(f"./data/net/{file_name}.py", "wb") as f:
        f.write(contents)
    try:
        Net.create(
            net_name=netName,
            node_name=user_info["username"],
            file_name=file_name,
            input_num=inputNum,
            output_num=outputNum,
            detail=detail,
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(400, f"上传失败，res:{e}")
    return {"status": "success"}


@net.get("/detail")
async def get_net_detail(request: Request):
    net_id = request.query_params.get("net_id")
    net = Net.select().where(Net.id == net_id).get()
    file_name = net.file_name
    with open(f"./data/net/{file_name}.py", "r") as f:
        code = f.read()
    return {"code": code}