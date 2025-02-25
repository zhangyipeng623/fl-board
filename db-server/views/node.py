from fastapi import APIRouter
from model import Node
import requests, psutil, torch
from utils.node import get_gpu_info

node = APIRouter(prefix="/node")


@node.get("/status")
def get_node():
    system_info = {}
    node_list = Node.select().order_by(Node.created_at.desc()).dicts()
    node_list = list(node_list)
    for node in node_list:
        node["name"] = node["node_name"]
        url = f"http://{node['ip']}:{node['port']}/status"
        try:
            if requests.get(url, timeout=3).status_code == 200:
                node["is_connect"] = True
            else:
                node["is_connect"] = False
        except:
            node["is_connect"] = False
        system_info[node["node_name"]] = {
            "cpu": node["cpu"],
            "gpu": node["gpu"],
            "system": node["system"],
        }
    return {"system": system_info, "node_list": node_list}


@node.get("/metrics")
def get_metrics():
    HAS_GPU = torch.cuda.is_available()
    cpu_usage = psutil.cpu_percent(interval=0.5)
    cpu_freq = psutil.cpu_freq().current / 1000  # 转换为GHz
    if HAS_GPU:
        gpu_info = get_gpu_info()
    else:
        gpu_info = {}
    return {
        "cpu": {
            "cpu_usage": cpu_usage,
            "cpu_freq": cpu_freq,
        },
        "gpu_info": gpu_info,
    }
