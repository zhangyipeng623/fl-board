from fastapi import APIRouter
from model import Net

net = APIRouter(prefix="/net")



@net.get("/list")
def get_net_list():
    # 获得网络模型列表
    database = Net.select().order_by(Net.updated_at.desc())
    net_list = list(database.dicts())

    return {"net_list": net_list}

