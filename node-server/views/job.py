from fastapi import APIRouter, Request, HTTPException
from config import config
from model import redis
import os
import requests
import json
from pydantic import BaseModel
from typing import List
job = APIRouter(prefix="/job")


class Field(BaseModel):
    field: str
    type: str


class JobInfo(BaseModel):
    job_id: str
    net_file: str
    aligned_file: str
    epochs: int
    input_field: List[Field]  # 使用定义好的Field模型
    output_field: Field  # 使用定义好的Field模型
    node_id: int


@job.post("/start")
def job_start(
    job: JobInfo,
):
    if not os.path.exists(f"./data/net/{job.net_file}.py"):
        res = requests.get(
            f"http://{config.center_host}:{config.center_port}/net/get_net_file?net_id={job.net_file}"
        )
        if res.status_code == 200:
            with open(f"./data/net/{job.net_file}.py", "wb") as f:
                f.write(res.content)
        else:
            raise HTTPException(
                status_code=400, detail="net file download failed")
    redis.lpush("job_list", json.dumps(job.model_dump()))
    return {"message": "job start"}


@job.get("/log/{job_id}")
async def get_job_log(job_id: str):
    """
    获取指定任务的日志

    参数:
        job_id: 任务ID

    返回:
        包含日志内容的JSON对象
    """
    try:
        # 构建日志文件路径
        log_file = os.path.join("./data/log", f"{job_id}.log")

        # 检查文件是否存在
        if not os.path.exists(log_file):
            return {"log": f"任务 {job_id} 的日志不存在"}

        # 读取日志文件内容
        with open(log_file, "r", encoding="utf-8") as f:
            log_content = f.read()

        return {"log": log_content}
    except Exception as e:
        # 记录错误并返回友好的错误信息
        print(f"获取日志时出错: {str(e)}")
        return {"log": f"获取日志时出错: {str(e)}"}
