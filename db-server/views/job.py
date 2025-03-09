import json
import uuid
import os
from typing import List, Optional
from fastapi import Request, APIRouter, HTTPException, Query
from pydantic import BaseModel
from model import Job, Ruler, Net, redis, User, DataBase, NodeJob


job = APIRouter(prefix="/job")


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


@job.get("/list")
def get_job_list():
    job_list = Job.select().order_by(Job.updated_at.desc())
    job_list = list(job_list.dicts())
    return {"job_list": job_list}


@job.post("/add")
def job_add(job_info: JobInfo, request: Request):
    session = request.headers.get("Authorization")
    user_info = json.loads(redis.get(session))
    user = User.select().where(
        User.username == user_info["username"], User.id == user_info["id"]).get_or_none()

    if user is None:
        raise HTTPException(400, detail="用户不存在")
    net = Net.select().where(Net.id == job_info.net).get_or_none()
    if net is None:
        raise HTTPException(400, detail="网络模型不存在")
    aligned_db = Ruler.select().where(Ruler.id == job_info.db).get_or_none()
    if aligned_db is None:
        raise HTTPException(400, detail="数据库不存在")

    job_id = uuid.uuid4()
    Job.create(
        net_id=job_info.net,
        net_name=net.net_name,
        db_id=job_info.db,
        db_name=aligned_db.aligned_db,
        node_name=user.node.nodename,
        input_field=[field.dict() for field in job_info.input_field],
        output_field=job_info.output_field.model_dump(),
        status="waiting",
        job_id=str(job_id),
        total=job_info.round,
        finished=0,
    )

    node_list = []

    for db_node in aligned_db.original_db:
        db_item = DataBase.select().where(
            DataBase.id == db_node["id"]).get_or_none()

        NodeJob.create(
            job_id=job_id,
            node_id=db_item.node.id,
            db_id=db_item.id,
            status="waiting",
            total=job_info.round * job_info.epochs + job_info.epochs,
            finished=0,
        )
        node_list.append(
            {"ip": db_item.node.ip, "port": db_item.node.port, "node_id": db_item.node.id})

    job = {
        "job_info": job_info.model_dump(),
        "job_id": str(job_id),
        "net_file_name": net.file_name,
        "aligned_db": aligned_db.file_name,
        "node_list": node_list,
    }

    redis.lpush("job_list", json.dumps(job))
    return {"status": "success"}


@job.get("/update")
def update_job(
        job_id: str = Query(..., description="任务ID"),
        label: str = Query(..., description="更新字段"),
        node: str = Query(..., description="节点ID"),
        data: str = Query(..., description="字段值")):
    if node == "center":
        job = Job.select().where(Job.job_id == job_id).get_or_none()
        if job is None:
            raise HTTPException(400, detail="任务不存在")
        if label == "status":
            job.status = data
        elif label == "progress":
            job.finished = int(data)
        job.save()
    else:
        node_job = NodeJob.select().where(
            NodeJob.job_id == job_id, NodeJob.node == int(node)).get_or_none()
        if node_job is None:
            raise HTTPException(400, detail="任务不存在")
        if label == "status":
            node_job.status = data
        elif label == "progress":
            node_job.finished = int(data)
        node_job.save()
    return {"status": "success"}


@job.get("/progress/{job_id}")
def get_job_progress(job_id: str):
    job = Job.select().where(Job.job_id == job_id).get_or_none()
    if job is None:
        raise HTTPException(400, detail="任务不存在")

    # 获取所有相关节点任务
    node_jobs = NodeJob.select().where(NodeJob.job_id == job_id)
    node_progress = []

    for node_job in list(node_jobs):
        node_progress.append({
            "node_name": node_job.node.nodename,
            "ip": node_job.node.ip,
            "port": node_job.node.port,
            "finished": node_job.finished,
            "total": node_job.total
        })

    return {
        "status": job.status,
        "center": {
            "finished": job.finished,
            "total": job.total
        },
        "nodes": node_progress
    }


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
