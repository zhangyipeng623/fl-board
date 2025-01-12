from fastapi import APIRouter
from fastapi import  HTTPException
from pydantic import BaseModel
from model import User
import psutil
import uuid


router = APIRouter()

class LoginForm(BaseModel):
    username: str
    password: str

@router.post("/login") # 根路由
def login(form: LoginForm):
    user = User.select().where(User.username == form.username, User.password == form.password).get()
    if(user is None):
        return HTTPException(status_code=401, detail="用户名或密码错误")

    return {"ip": user.ip, "port": user.port,"session": uuid.uuid4()}

@router.get("/status")
def get_status():
    status = {
        "mysql":False,
        "redis":False,
        "nginx":False
    }
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'mysqld':  # mysqld是MySQL服务的主要进程名
            status["mysql"] = True
        if proc.info['name'] == 'redis-server':
            status["redis"] = True
        if proc.info['name'] == 'nginx':
            status["nginx"] = True
    return {"data": status}

