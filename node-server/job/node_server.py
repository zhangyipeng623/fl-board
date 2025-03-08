import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
import flwr as fl
import logging
import importlib
from typing import Tuple

# 配置设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def init_net(net_id) -> Tuple[nn.Module, Dataset]:
    """动态加载完网络模型"""
    try:
        module = importlib.import_module(f"data.net.{net_id}")
        #
        net_class = getattr(module, "Net")
        dataset_class = getattr(module, "DataSet")
        if not issubclass(net_class, nn.Module):
            raise ValueError(f"{net_id} 不是有效网络模型")
        if not issubclass(dataset_class, Dataset):
            raise ValueError(f"{net_id} 不是有效数据集")
        return net_class, dataset_class
    except (ImportError, AttributeError) as e:
        logging.error(f"网络模型加载失败: {str(e)}")
        raise


# 客户端类
class FlowerClient(fl.client.NumPyClient):
    def __init__(self, trainloader, model, logger):
        self.model = model.to(device)
        self.trainloader = trainloader
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.01)
        self.logger = logger

    def get_parameters(self, config):
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v).to(device) for k, v in params_dict}
        self.model.load_state_dict(state_dict)

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        self.model.train()
        current_round = config.get("current_round", 0)

        self.logger.info(f"\n=== 第 {current_round} 轮参数交换后的训练 ===")
        _, _, data = self.evaluate(parameters, config)
        self.logger.info(
            f"[第{current_round}轮初始] Loss: {float(data['loss']):.4f}, Acc: {float(data['acc']):.4f}"
        )

        for epoch in range(5):  # 本地训练5个epoch
            total_loss = 0.0
            correct = 0.0
            total = 0
            for inputs, labels in self.trainloader:
                self.optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()

                # 累计指标
                total_loss += loss.item() * inputs.size(0)
                _, predicted = torch.max(outputs, 1)
                correct += (predicted == labels).sum().item()
                total += labels.size(0)

            # 每个epoch输出
            epoch_loss = total_loss / total
            epoch_acc = correct / total
            self.logger.info(
                f"第{current_round}轮 - Epoch {epoch+1} - Loss: {epoch_loss:.4f}, Acc: {epoch_acc:.4f}"
            )

        _, _, finally_data = self.evaluate(parameters, config)
        self.logger.info(
            f"[第{current_round}轮最终] Loss: {float(finally_data['loss']):.4f}, Acc: {float(finally_data['acc']):.4f}"
        )
        return self.get_parameters(config={}), len(self.trainloader.dataset), {}

    def evaluate(self, parameters, config):
        """辅助方法用于评估模型"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in self.trainloader:
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                total_loss += loss.item() * inputs.size(0)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        return (
            float(total_loss / total),
            total,
            {"acc": correct / total, "loss": total_loss / total},
        )


# 数据加载函数
def load_data(file_path, dataset, device):
    # 假设所有客户端共享同一个数据文件，根据ID划分
    df = pd.read_csv(file_path)
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values

    le = LabelEncoder()
    y = le.fit_transform(y)

    return dataset(X, y, device)


def start(net, logger, aligned_db):

    # 设置全局 Logger，将 Flower 使用的日志也输出到 job 的日志中
    flwr_logger = logging.getLogger("flwr")  # Flower 日志
    flwr_logger.setLevel(logging.INFO)  # 设置日志级别
    flwr_logger.propagate = False

    # 将 job_logger 的 handler 添加到 Flower logger
    for handler in logger.handlers:
        flwr_logger.addHandler(handler)

    net_class, dataset_class = init_net(net)
    net_class = net_class()
    dataset = load_data(
        f"./data/aligned/{aligned_db}.csv", dataset_class, device)
    trainloader = DataLoader(dataset, batch_size=8, shuffle=True)
    fl.client.start_numpy_client(
        server_address="127.0.0.1:10001",
        grpc_max_message_length=10*1024*1024*10244,
        client=FlowerClient(trainloader, net_class, logger).to_client(),
    )
