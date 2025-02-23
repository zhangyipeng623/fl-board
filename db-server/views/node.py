from fastapi import APIRouter
from model import Node
import requests, psutil, torch

node = APIRouter(prefix="/node")


def get_gpu_info():
    import pynvml

    # 初始化 NVML 库，该库用于与 NVIDIA GPU 进行交互
    pynvml.nvmlInit()

    # 获取系统中可用的 NVIDIA GPU 设备数量
    device_count = pynvml.nvmlDeviceGetCount()

    gpu_info = {}
    for i in range(device_count):
        # 根据索引获取每个 GPU 设备的句柄，后续操作需要通过句柄来访问该 GPU
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)

        # 获取 GPU 的名称，并将其从字节类型解码为字符串类型
        gpu_name = pynvml.nvmlDeviceGetName(handle).decode("utf-8")

        # 获取 GPU 的内存信息，包括总内存、已使用内存和空闲内存
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)

        # 获取 GPU 的当前温度，第二个参数 0 表示使用默认的温度传感器
        temperature = pynvml.nvmlDeviceGetTemperature(handle, 0)

        # 获取 GPU 当前的核心频率，NVML_CLOCK_GRAPHICS 表示核心频率
        core_frequency = pynvml.nvmlDeviceGetClockInfo(
            handle, pynvml.NVML_CLOCK_GRAPHICS
        )

        # 获取 GPU 当前的显存频率，NVML_CLOCK_MEM 表示显存频率
        memory_frequency = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)

        # 将获取到的 GPU 信息存储在字典中
        gpu_info[f"{gpu_name}"] = {
            "memory_info": memory_info,
            "temperature": temperature,
            "core_frequency": core_frequency,
            "memory_frequency": memory_frequency,
        }

    # 关闭 NVML 库，释放相关资源
    pynvml.nvmlShutdown()

    return gpu_info


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


@node.post("/metrics")
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
