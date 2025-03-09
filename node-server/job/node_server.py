import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import IterableDataset, DataLoader
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
import flwr as fl
import logging
import importlib
from typing import Tuple
from pydantic import BaseModel
from typing import List
from config import config
import requests
import time

# 配置设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def update_jop_data(data, job_id, node_id, logger):
    """更新数据"""
    url = f"http://{config.center_host}:{config.center_port}/job/update?label=progress&job_id={job_id}&node={node_id}&data={data}"
    try:
        # 设置超时时间为5秒，避免请求无限等待
        res = requests.get(url, timeout=500)
        if res.status_code == 200:
            logger.info("任务数据更新成功")
        else:
            logger.error("任务数据更新失败")
    except requests.Timeout:
        # 请求超时处理
        logger.error(f"更新任务数据超时: job_id={job_id}, round={round}")
    except requests.RequestException as e:
        # 其他请求异常处理
        logger.error(f"更新任务数据失败: {str(e)}")


def init_net(net_id) -> Tuple[nn.Module, dict]:
    """动态加载网络模型和转换函数"""
    try:
        module = importlib.import_module(f"data.net.{net_id}")

        # 获取网络类和四个转换函数
        net_class = getattr(module, "Net")
        transform_x = getattr(module, "transform_x")  # 特征转换函数
        transform_y = getattr(module, "transform_y")  # 标签转换函数
        optimizer = getattr(module, "get_optimizer")  # 优化器工厂
        criterion = getattr(module, "get_criterion")  # 损失函数工厂

        # 验证类型
        if not issubclass(net_class, nn.Module):
            raise ValueError(f"{net_id} 不是有效网络模型")
        if not all(callable(f) for f in [transform_x, transform_y, optimizer, criterion]):
            raise ValueError(f"{net_id} 模块缺少必需的转换函数或工厂方法")

        return net_class, {
            'transform_x': transform_x,
            'transform_y': transform_y,
            'optimizer': optimizer,
            'criterion': criterion
        }
    except (ImportError, AttributeError) as e:
        logging.error(f"网络模型加载失败: {str(e)}")
        raise


# 客户端类
class FlowerClient(fl.client.NumPyClient):
    def __init__(self, trainloader, model, logger, criterion, optimizer, epochs, node_id, job_id):
        self.model = model.to(device)
        self.trainloader = trainloader
        self.criterion = criterion
        self.optimizer = optimizer
        self.epochs = epochs
        self.logger = logger
        self.node_id = node_id
        self.job_id = job_id

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

        # 记录处理的样本数
        samples_processed = 0

        for epoch in range(self.epochs):  # 本地训练5个epoch
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
                batch_size = inputs.size(0)
                if epoch == 0:
                    samples_processed += batch_size
                total_loss += loss.item() * batch_size
                _, predicted = torch.max(outputs, 1)
                correct += (predicted == labels).sum().item()
                total += batch_size

            # 每个epoch输出
            epoch_loss = total_loss / total
            epoch_acc = correct / total
            self.logger.info(
                f"第{current_round}轮 - Epoch {epoch+1} - Loss: {epoch_loss:.4f}, Acc: {epoch_acc:.4f}"
            )
            # 更新进度
            update_jop_data(current_round*self.epochs+epoch+1,
                            self.job_id, self.node_id, self.logger)
            time.sleep(0.2)
        _, _, finally_data = self.evaluate(parameters, config)
        self.logger.info(
            f"[第{current_round}轮最终] Loss: {float(finally_data['loss']):.4f}, Acc: {float(finally_data['acc']):.4f}"
        )
        # 返回处理的样本数而不是数据集长度
        return self.get_parameters(config={}), samples_processed, {}

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


class StreamingDataset(IterableDataset):
    def __init__(self, file_path, transform_x, transform_y, input_field, output_field, chunk_size=1000):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.transform_x = transform_x
        self.transform_y = transform_y
        self.input_field = input_field
        self.output_field = output_field

    def __iter__(self):
        # 使用 pandas 分块读取数据
        for chunk in pd.read_hdf(self.file_path, 'df', chunksize=self.chunk_size):
            input_cols = []
            for field in self.input_field:
                col = chunk[field.field].astype(field.type)
                input_cols.append(col)
            X = pd.concat(input_cols, axis=1).values

            # 处理多输出字段
            y = chunk[self.output_field.field].astype(
                self.output_field.type).values

            # 对每个批次进行预处理
            X = self.transform_x(X)
            y = self.transform_y(y)

            for i in range(len(X)):
                yield X[i], y[i]


class Field(BaseModel):
    field: str
    type: str


class JobInfo(BaseModel):
    node_id: int
    job_id: str
    net_file: str
    aligned_file: str
    epochs: int
    input_field: List[Field]
    output_field: Field


def start(job, logger):
    # 转换字典为 Pydantic 模型
    try:
        logger.info("任务参数验证成功: %s", job)
        try:
            job_info = JobInfo(**job)  # 使用新变量名避免冲突
        except Exception as e:
            logger.error(f"任务参数验证失败: {str(e)}")
            raise
        logger.info("任务参数验证成功: %s", job_info)
        # 设置全局 Logger
        flwr_logger = logging.getLogger("flwr")
        flwr_logger.setLevel(logging.INFO)
        flwr_logger.propagate = False
        # 加载网络模型
        net_class, function = init_net(job_info.net_file)  # 使用转换后的模型对象
        model = net_class()
        # 创建优化器和损失函数
        optimizer = function['optimizer'](model)  # 传入模型参数创建优化器
        criterion = function['criterion']()  # 创建损失函数实例
        # 加载数据集
        dataset = StreamingDataset(
            f"./data/aligned/{job_info.aligned_file}.h5",  # 使用模型字段
            function['transform_x'],
            function['transform_y'],
            job_info.input_field,
            job_info.output_field
        )
        trainloader = DataLoader(dataset, batch_size=32)

        fl.client.start_numpy_client(
            server_address="127.0.0.1:10001",
            client=FlowerClient(trainloader, model, logger,
                                criterion, optimizer, job_info.epochs, job_info.node_id, job_info.job_id).to_client(),
        )
    except Exception as e:
        logger.error("任务启动失败: %s", str(e))
        raise
