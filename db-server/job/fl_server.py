import flwr as fl
import torch
import torch.nn as nn
import requests
from typing import Dict, List, Optional, Tuple
from flwr.server.strategy import Strategy
from flwr.common import parameters_to_ndarrays
import logging
import importlib
from pydantic import BaseModel
from config import config
import time


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_fit_config(server_round: int) -> Dict[str, int]:
    return {"current_round": server_round}


def init_strategy(name: str) -> type:
    """动态加载策略类（返回类而非实例）"""
    try:
        module = importlib.import_module("flwr.server.strategy")
        strategy_class = getattr(module, name)
        if not issubclass(strategy_class, Strategy):
            raise ValueError(f"{name} 不是有效策略类型")
        return strategy_class
    except (ImportError, AttributeError) as e:
        logging.error(f"策略加载失败: {str(e)}")
        raise


def init_net(net_id) -> nn.Module:
    """动态加载完网络模型"""
    try:
        module = importlib.import_module(f"data.net.{net_id}")
        net_class = getattr(module, "Net")
        if not issubclass(net_class, nn.Module):
            raise ValueError(f"{net_id} 不是有效网络模型")
        return net_class
    except (ImportError, AttributeError) as e:
        logging.error(f"网络模型加载失败: {str(e)}")
        raise


def update_jop_data(round, job_id):
    """更新数据"""
    url = f"http://{config.Host}:{config.Port}/job/update?label=progress&job_id={job_id}&node=center&data={round}"
    try:
        # 设置超时时间为5秒，避免请求无限等待
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            logging.info(f"更新任务数据成功: job_id={job_id}, round={round}")
        else:
            logging.error(f"更新任务数据失败: job_id={job_id}, round={round}")
    except requests.Timeout:
        # 请求超时处理
        logging.error(f"更新任务数据超时: job_id={job_id}, round={round}")
    except requests.RequestException as e:
        # 其他请求异常处理
        logging.error(f"更新任务数据失败: {str(e)}")


def create_custom_strategy(
        strategy_class: type, model: nn.Module, logger, job_id, device="cpu", **kwargs) -> type:
    """创建继承自指定策略类的自定义策略"""

    class CustomStrategy(strategy_class):  # 继承策略类
        def __init__(self, model: nn.Module, logger, job_id, device, *args, **kwargs):
            # 显式传递所有必要参数给父类
            super().__init__(*args, **kwargs)
            self.model = model
            self.device = device
            self.job_id = job_id
            self.logger = logger

        def aggregate_fit(
            self,
            server_round: int,
            results: List[Tuple[fl.server.client_proxy.ClientProxy, fl.common.FitRes]],
            failures: List[BaseException],
        ) -> Tuple[Optional[fl.common.Parameters], Dict[str, fl.common.Scalar]]:
            # 调用父类聚合方法
            aggregated_parameters, aggregated_metrics = super().aggregate_fit(
                server_round, results, failures
            )

            if aggregated_parameters:
                try:
                    self._save_model(server_round, aggregated_parameters)
                except Exception as e:
                    self.logger.error(f"模型保存失败: {e}", exc_info=True)
            update_jop_data(server_round, self.job_id)
            time.sleep(1)
            return aggregated_parameters, aggregated_metrics

        def _save_model(self, round_num: int, parameters: fl.common.Parameters):
            """安全保存模型"""
            # 参数转换
            ndarrays = parameters_to_ndarrays(parameters)
            state_dict = {
                k: torch.tensor(v).to(self.device)
                for k, v in zip(self.model.state_dict().keys(), ndarrays)
            }

            # 加载参数
            self.model.load_state_dict(state_dict, strict=True)

            save_path = f"./data/model/{self.job_id}/round_{round_num}.pth"
            torch.save(self.model.state_dict(), save_path)

            self.logger.info(f"模型保存成功: {save_path}")

    return CustomStrategy(
        model=model,
        logger=logger,
        job_id=job_id,
        device=device,
        **kwargs,
    )  # 实例化自定义策略


class ServerConfig(BaseModel):
    fraction_fit: float = 1.0
    fraction_evaluate: float = 1.0
    min_fit_clients: int = 1
    min_evaluate_clients: int = 1
    min_available_clients: int = 1
    min_completion_rate_fit: float = 1.0
    min_completion_rate_evaluate: float = 1.0
    accept_failure: bool = False


class Field(BaseModel):
    field: str
    type: str


class JobInfo(BaseModel):
    db: int
    input_field: List[Field]
    output_field: Field
    net: int
    round: int = 10
    epochs: int = 5
    strategy: str = "FedAvg"
    server_config: Optional[ServerConfig]


def start(net_id, job_id, logger, info):
    try:
        # 初始化模型
        logging.info("任务参数验证成功: {%s}", info)
        model = init_net(net_id)
        model = model().to(device)
        # 加载策略类并创建自定义策略
        try:
            logger.info("任务参数验证成功: {%s}", info)
            job_info = JobInfo(**info)  # 使用新变量名避免冲突
        except Exception as e:
            logger.error("任务参数验证失败: %s", str(e))
        print(job_info)
        logger.info("任务参数验证成功: {%s}", job_info)
        strategy_class = init_strategy(job_info.strategy)

        # 根据策略类型设置参数
        strategy_params = {
            "fraction_fit": job_info.server_config.fraction_fit,
            "fraction_evaluate": job_info.server_config.fraction_evaluate,
            "min_fit_clients": job_info.server_config.min_fit_clients,
            "min_evaluate_clients": job_info.server_config.min_evaluate_clients,
            "min_available_clients": job_info.server_config.min_available_clients,
            "on_fit_config_fn": get_fit_config,
        }

        # 只有特定策略支持这些参数
        if job_info.strategy in ["FedAdagrad", "FedAdam", "FedYogi"]:
            strategy_params.update({
                "min_completion_rate_fit": job_info.server_config.min_completion_rate_fit,
                "min_completion_rate_evaluate": job_info.server_config.min_completion_rate_evaluate,
                "accept_failure": job_info.server_config.accept_failure
            })

        strategy = create_custom_strategy(
            strategy_class,
            model,
            logger,
            job_id=job_id,
            device=device,
            **strategy_params
        )
        # 配置 Flower 日志以写入同一个日志文件
        flower_logger = logging.getLogger("flwr")
        flower_logger.setLevel(logging.INFO)  # 设置日志级别
        for handler in logger.handlers:  # 将 job 的所有 handlers 共享给 Flower
            flower_logger.addHandler(handler)

        # 启动服务器
        fl.server.start_server(
            server_address="127.0.0.1:10001",
            config=fl.server.ServerConfig(num_rounds=job_info.round),
            strategy=strategy,
        )
    except Exception as e:
        print(f"任务执行失败: {str(e)}")
        logger.error("服务器启动失败: %s", str(e), exc_info=True)
