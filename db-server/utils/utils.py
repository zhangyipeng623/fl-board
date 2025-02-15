import flwr as fl
import torch
import torch.nn as nn
from typing import Dict
from sklearn.preprocessing import StandardScaler
from torch.utils.data import Dataset
import logging


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 定义一个函数，用于在每一轮训练开始时传递轮次信息
def get_fit_config(server_round: int) -> Dict[str, int]:
    return {"current_round": server_round}  # 将轮次信息传递给客户端

# 评估函数
def start(file_name):
    #设置📔
    logging.basicConfig(
        filename=f'./data/log/{file_name}.log',  # 新增：输出日志到文件
        level=logging.INFO,  # 新增：日志级别
        format='%(asctime)s - %(levelname)s - %(message)s',  # 新增：日志格式
    )

    # 定义联邦策略
    strategy = fl.server.strategy.FedAvg(
        fraction_fit=1.0,
        fraction_evaluate=1, 
        min_fit_clients=1,
        min_available_clients=1,
        min_evaluate_clients=1,
        on_fit_config_fn=get_fit_config,  # 设置回调函数
    )
    
    # 启动服务器
    fl.server.start_server(
        server_address="0.0.0.0:10001",
        config=fl.server.ServerConfig(num_rounds=10),
        strategy=strategy,
    )

if __name__ == "__main__":
    # 开启新进程开启服务
    import multiprocessing
    p = multiprocessing.Process(target=start)
    p.daemon = False 
    p.start()
    print("Server started")
