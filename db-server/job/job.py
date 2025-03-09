from model import redis
from config import config
from .fl_server import start  # 使用显式相对导入
import requests
import logging
import time
import json
import os


def update_job_status(status, logger, job_id):
    url = f"http://{config.Host}:{config.Port}/job/update?label=status&job_id={job_id}&node=center&data={status}"
    try:
        # 设置超时时间为5秒，避免请求无限等待
        res = requests.get(url, timeout=5000)
        if res.status_code == 200:
            logger.info("更新任务数据成功: job_id=%s",
                        str(job_id))
        else:
            logger.error("更新任务数据失败: job_id=%s",
                         str(job_id))
    except requests.Timeout:
        # 请求超时处理
        logger.error("更新任务数据超时: job_id=%s", str(job_id))
    except requests.RequestException as e:
        # 其他请求异常处理
        logger.error("更新任务数据失败: %s", str(e))


def start_job():
    while True:
        job = redis.rpop("job_list")
        if job is None:
            time.sleep(1)
            continue
        job = json.loads(job)  # # 获取job

        model_dir = job.get("model_dir", f"./data/model/{job.get('job_id')}")
        os.makedirs(model_dir, exist_ok=True)

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

        node_list = job.get("node_list")
        for node in node_list:
            # 构建请求参数
            json_data = {
                "node_id": node['node_id'],
                'job_id': job.get('job_id'),
                'net_file': job.get('net_file_name'),
                'aligned_file': job.get('aligned_db'),
                'epochs': job.get('job_info').get('epochs'),
                "input_field": job.get('job_info').get('input_field'),
                "output_field": job.get('job_info').get('output_field'),
            }
            logger.info("%s", json.dumps(json_data))
            try:
                base_url = f"http://{node['ip']}:{node['port']}/job/start"
                # 正确使用POST请求
                res = requests.post(  # 修改为post方法
                    base_url,
                    headers={
                        "x-forwarded-for": config.Host
                    },
                    json=json_data,  # 直接传递JSON参数
                    timeout=100
                )
                if res.status_code == 200:
                    logger.info("%s:%s start job success",
                                node['ip'], node['port'])
                    print(
                        (f"{node['ip']}:{node['port']} start job success"))
                else:
                    logger.error("%s:%s start job fail",
                                 node['ip'], node['port'])
                    print((f"{node['ip']}:{node['port']} start job fail"))
            except requests.Timeout:
                logger.error("%s:%s request timeout", node['ip'], node['port'])
                print((f"{node['ip']}:{node['port']} request timeout"))
            except requests.RequestException as e:
                logger.error("%s:%s request error: %s",
                             node['ip'], node['port'], str(e))
                print((f"{node['ip']}:{node['port']} request error: {str(e)}"))
                print((f"{node['ip']}:{node['port']} request error: {str(e)}"))

        update_job_status("running", logger, job.get('job_id'))

        # 启动对应的任务，并记录日志
        try:
            logger.info("任务开始执行")
            logger.info("任务参数: {%s}", json.dumps(job.get("job_info")))
            start(job.get("net_file_name"), job.get(
                "job_id"), logger, job.get("job_info"))
            update_job_status("finished", logger, job.get('job_id'))
        except Exception as e:
            print(f"任务执行失败: {str(e)}")
            logger.error("任务执行失败: {%s}", str(e))
        finally:
            # 任务结束后移除 Handler，避免资源泄露
            logger.removeHandler(file_handler)
            file_handler.close()
