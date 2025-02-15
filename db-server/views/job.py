from fastapi import APIRouter,HTTPException
from model import Job,redis
from fastapi import UploadFile, File, Form,Request
import ast,uuid, json
from ast import ClassDef
from typing import List

job = APIRouter(prefix="/job")


@job.get("/list")
def get_job_list(request: Request):
    job_list = Job.select().order_by(Job.updated_at.desc())
    job_list = list(job_list.dicts())
    return {"job_list": job_list}

@job.post("/add")
def job_add(request: Request):
    pass