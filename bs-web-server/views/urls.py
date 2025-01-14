from fastapi import APIRouter,HTTPException,Request
from pydantic import BaseModel
from model import User,redis
import psutil
import uuid
import json

router = APIRouter()

class LoginForm(BaseModel):
    username: str
    password: str

@router.post("/login") # 根路由
def login(form: LoginForm):
    user = User.select().where(User.username == form.username, User.password == form.password).get()
    if(user is None):
        return HTTPException(status_code=401, detail="用户名或密码错误")
    session = str(uuid.uuid4())
    user_info = json.dumps({"username": user.username, "id": user.id,"ip":user.ip,"port":user.port})
    redis.set(session, user_info, ex=60*60*24*2)
    return {"ip": user.ip, "port": user.port,"session": session}

@router.get("/status")
def get_status():
    from model import db
    from peewee import OperationalError

    status = {
        "mysql":False,
        "redis":False,
        "nginx":False
    }
    try:
        db.connect()
        status["mysql"] = True
        print("mysql连接成功")
    except OperationalError:
        status["mysql"] = False
        print("mysql连接失败")
    finally:
        if status["mysql"] == True:
            db.close()  # 确保连接关闭

    # 检查 Redis 连接
    try:
        redis.ping()  # 发送 PING 命令
        status["redis"] = True
        print("redis连接成功")
    except:
        status["redis"] = False
        print("redis连接失败")

    # 检查 nginx 服务
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'nginx':
            status["nginx"] = True
    print(status,"status")
    return {"data": status}

@router.get("/check_session")
def check_session(request: Request):
    session = request.query_params.get("session")
    user_info = redis.get(session)
    if(user_info is None):
        return HTTPException(status_code=401, detail="用户未登录")
    return {"user_info": user_info}

@router.get("/logout")
def logout(request: Request):
    session = request.query_params.get("session")
    redis.delete(session)
    return {"message": "用户已退出"}