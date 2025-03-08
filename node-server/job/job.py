import logging
import time
import json
import os
from model import redis
from job.node_server import start


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
            start(job.get("net_file"), logger, job.get("aligned_db"))
        finally:
            # 任务结束后移除 Handler，避免资源泄露
            logger.removeHandler(file_handler)
            file_handler.close()

        time.sleep(1)
