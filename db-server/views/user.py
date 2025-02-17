from fastapi import APIRouter,HTTPException,Request
from pydantic import BaseModel
from peewee import OperationalError
from model import User,redis,db
import json, psutil, uuid


user = APIRouter()

class LoginForm(BaseModel):
    username: str
    password: str

@user.post("/login") # 根路由
def login(form: LoginForm):
    user = User.select().where(User.username == form.username, User.password == form.password).get()
    if(user is None):
        raise HTTPException(401, detail="用户名或密码错误")
    session = str(uuid.uuid4())
    user_info = json.dumps({"ip": user.ip, "port": user.port,"username": user.username,"id": user.id})
    redis.set(session, user_info, ex=60*60*24*2)
    return {"ip": user.ip, "port": user.port, "session": session,"id": user.id}

@user.get("/status")
def get_status():


    status = {
        "mysql":False,
        "redis":False,
        "nginx":False
    }
    # ---------- 检查 MySQL 连接 ----------
    try:
        # 使用 connection_context 自动管理连接
        with db.connection_context():  # 注意：移除了 reuse_if_open 参数
            db.execute_sql("SELECT 1")  # 执行真实查询验证连接
            status["mysql"] = True
    except OperationalError as e:
        status["mysql"] = False

    # ---------- 检查 Redis 连接 ----------
    try:
        # 使用更具体的异常类型（如 redis.ConnectionError）
        redis.ping()  # 假设 redis_client 是已配置的客户端
        status["redis"] = True
    except redis.ConnectionError as e:
        status["redis"] = False

    # ---------- 检查 Nginx 进程 ----------
    try:
        # 更可靠的方式：检查 80 端口是否被监听
        for conn in psutil.net_connections(kind='tcp'):
            if conn.status == 'LISTEN' and conn.laddr.port == 80:
                # 确认监听进程是 Nginx
                process = psutil.Process(conn.pid)
                if "nginx" in process.name().lower():
                    status["nginx"] = True
                    break
    except Exception as e:
        status["nginx"] = False
    return {"data": status}

@user.get("/check_session")
def check_session(request: Request):
    session = request.query_params.get("session")
    user_info = redis.get(session)
    if(user_info is None):
        raise HTTPException(401, detail="用户未登录")
    user_info = json.loads(user_info)
    return {"ip": user_info["ip"], "port": user_info["port"],"username": user_info["username"],"id": user_info["id"]}

@user.get("/logout")
def logout(request: Request):
    session = request.query_params.get("session")
    redis.delete(session)
    return {"message": "用户已退出"}