import flwr as fl
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple
from flwr.server.strategy import Strategy
from flwr.common import parameters_to_ndarrays
import logging, importlib


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


def create_custom_strategy(
    strategy_class: type, model: nn.Module, logger, job_id, device="cpu", **kwargs
) -> type:
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


def start(net_id, job_id, logger):

    # 初始化模型
    model = init_net(net_id)
    model = model().to(device)
    # 加载策略类并创建自定义策略
    strategy_class = init_strategy("FedAvg")
    strategy = create_custom_strategy(
        strategy_class,
        model,
        logger,
        job_id=job_id,
        device=device,
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=1,
        min_evaluate_clients=1,
        min_available_clients=1,
        on_fit_config_fn=get_fit_config,
    )

    # 配置 Flower 日志以写入同一个日志文件
    flower_logger = logging.getLogger("flwr")
    flower_logger.setLevel(logging.INFO)  # 设置日志级别
    for handler in logger.handlers:  # 将 job 的所有 handlers 共享给 Flower
        flower_logger.addHandler(handler)

    # 启动服务器
    fl.server.start_server(
        server_address="0.0.0.0:10001",
        config=fl.server.ServerConfig(num_rounds=10),
        strategy=strategy,
    )


if __name__ == "__main__":
    import multiprocessing

    p = multiprocessing.Process(target=start, kwargs={"file_name": "server"})
    p.daemon = False
    p.start()
    print("Server started")
