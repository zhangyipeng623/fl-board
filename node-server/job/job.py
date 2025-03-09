import logging
import time
import json
import os
import requests
from model import redis
from .node_server import start
from config import config


def update_job_status(job_id, node_id, status, logger):
    base_url = f"http://{config.center_host}:{config.center_port}/job/update"
    params = {
        "label": "status",
        "job_id": job_id,
        "node": node_id,
        "data": status
    }
    url = f"{base_url}?" + "&".join(f"{k}={v}" for k, v in params.items())
    try:
        # 设置超时时间为5秒，避免请求无限等待
        res = requests.get(url, timeout=500)
        if res.status_code == 200:
            logger.info("任务状态更新成功")
        else:
            logger.error("任务状态更新失败")
    except requests.Timeout:
        # 请求超时处理
        logger.error(f"更新任务数据超时: job_id={job_id}")
    except requests.RequestException as e:
        # 其他请求异常处理
        logger.error(f"更新任务数据失败: {str(e)}")


def start_job():
    while True:
        job = redis.rpop("job_list")
        if job is None:
            time.sleep(1)
            continue
        job = json.loads(job)  # # 获取job

        # 动态获取日志文件存储目录
        log_dir = job.get(
            "log_dir", "./data/log/"
        )  # 从job中获取日志目录，缺省为"./data/log/"
        os.makedirs(log_dir, exist_ok=True)  # 如果目录不存在，则创建

        # 为每个 job 动态创建 Logger
        logger = logging.getLogger(
            f"job_{job.get('job_id')}"
        )  # 为每个job创建独特的Logger命名
        logger.setLevel(logging.INFO)

        # 创建 FileHandler，设置日志路径
        log_file = os.path.join(log_dir, f'{job.get("job_id")}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # 设置日志格式
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # 将 FileHandler 添加到 Logger
        logger.addHandler(file_handler)

        # 启动对应的任务，并记录日志
        try:
            update_job_status(job.get("job_id"), job.get(
                "node_id"), "running", logger)
            start(job, logger=logger)
            update_job_status(job.get("job_id"), job.get(
                "node_id"), "finished", logger)
        except Exception as e:
            logger.error("任务执行失败: %s", str(e))
        finally:

            logger.removeHandler(file_handler)
            file_handler.close()

        time.sleep(1)
