from fastapi import APIRouter, Request, HTTPException
from config import config
from model import redis
import os, requests, json

job = APIRouter(prefix="/job")


@job.get("/start")
def job_start(request: Request):
    job_id = request.query_params.get("job_id")
    net_file = request.query_params.get("net_id")
    aligned_db = request.query_params.get("aligned_db")
    if not os.path.exists(f"./data/net/{net_file}.py"):
        res = requests.get(
            f"http://{config.center_host}:{config.center_port}/net/get_net_file?net_id={net_file}"
        )
        if res.status_code == 200:
            with open(f"./data/net/{net_file}.py", "wb") as f:
                f.write(res.content)
        else:
            raise HTTPException(status_code=400, detail="net file download failed")
    job = {"job_id": job_id, "net_file": net_file, "aligned_db": aligned_db}
    redis.lpush("job_list", json.dumps(job))
    return {"message": "job start"}
