from fastapi import APIRouter, HTTPException
from model import Job, Ruler, Net, redis, User
from fastapi import Request
from pydantic import BaseModel
import json, uuid, requests

job = APIRouter(prefix="/job")


class Item(BaseModel):
    db: int
    input_field: list
    output_field: list
    net: int


@job.get("/list")
def get_job_list():
    job_list = Job.select().order_by(Job.updated_at.desc())
    job_list = list(job_list.dicts())
    return {"job_list": job_list}


@job.post("/add")
def job_add(job_info: Item, request: Request):
    session = request.headers.get("session")
    user_info = json.loads(redis.get(session))

    net = Net.select().where(Net.id == job_info.net).first()
    if net is None:
        raise HTTPException(400, detail="网络模型不存在")
    aligned_db = Ruler.select().where(Ruler.id == job_info.db).first()
    if aligned_db is None:
        raise HTTPException(400, detail="数据库不存在")
    job_id = uuid.uuid4()
    Job.create(
        net_id=job_info.net,
        net_name=net.net_name,
        db_id=job_info.db,
        db_name=aligned_db.aligned_db,
        node_name=user_info["username"],
        input_field=",".join(job_info.input_field),
        output_field=",".join(job_info.output_field),
        status="waiting",
        job_id=job_id,
    )

    original_db = aligned_db.original_db.split(",")
    node_list = []
    for db_node in original_db:
        _, node = db_node.split("-")
        user = User.select().where(User.username == node).first()
        node_list.append({"ip": user.node.ip, "port": user.node.port})

    job = {
        "job_id": str(job_id),
        "net_file_name": net.file_name,
        "aligned_db": aligned_db.file_name,
        "node_list": node_list,
    }

    redis.lpush("job_list", json.dumps(job))
    return {"status": "success"}
