from fastapi import APIRouter
import psutil, torch
from utils.node import get_gpu_info

node = APIRouter(prefix="/node")


@node.get("/metrics")
def get_metrics():
    HAS_GPU = torch.cuda.is_available()
    cpu_usage = psutil.cpu_percent(interval=0.5)
    cpu_freq = psutil.cpu_freq().current / 1000  # 转换为GHz
    if HAS_GPU:
        gpu_info = get_gpu_info()
    else:
        gpu_info = []
    return {
        "cpu": {
            "cpu_usage": cpu_usage,
            "cpu_freq": cpu_freq,
        },
        "gpu_info": gpu_info,
    }
