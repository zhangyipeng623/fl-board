from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from peewee import OperationalError
from model import User, redis, db
from config import config
import json, psutil, uuid, bcrypt, requests


user = APIRouter()


class LoginForm(BaseModel):
    username: str
    password: str


class RegisterForm(BaseModel):
    username: str
    password: str
    ip: str
    port: int


@user.post("/register")
def register_user(form: RegisterForm):
    """
    新增用户注册接口，演示如何加密保存密码
    """
    user = User.get_or_none(User.username == form.username)
    if user is not None:
        raise HTTPException(status_code=400, detail="用户名已存在")
    hashed_password = bcrypt.hashpw(
        form.password.encode("utf-8"), bcrypt.gensalt()
    )  # 加密密码
    new_user = User.create(
        username=form.username,
        password=hashed_password.decode("utf-8"),  # 存储解码后的加密哈希
        ip=form.ip,
        port=form.port,
    )
    return {"message": "用户注册成功", "username": new_user.username}


@user.post("/login")  # 根路由
def login(form: LoginForm):

    try:
        # 从数据库获取用户信息
        user = User.select().where(User.username == form.username).get()
        # 校验密码是否匹配
        if not bcrypt.checkpw(
            form.password.encode("utf-8"), user.password.encode("utf-8")
        ):
            raise HTTPException(401, detail="用户名或密码错误")
    except User.DoesNotExist:
        raise HTTPException(401, detail="用户名或密码错误")
    session = str(uuid.uuid4())
    user_info = json.dumps(
        {"ip": user.ip, "port": user.port, "username": user.username, "id": user.id}
    )
    redis.set(session, user_info, ex=60 * 60 * 24 * 2)
    login_info = {
        "ip": user.ip,
        "port": user.port,
        "username": user.username,
        "id": user.id,
        "session": session,
    }
    res = requests.post(
        f"http://{user.ip}:{user.port}/login",
        json=login_info,
        headers={"x-forwarded-for": config.Host},
    )
    if res.status_code != 200:
        raise HTTPException(401, detail=f"登陆出错{res.text}")
    return {"ip": user.ip, "port": user.port, "session": session, "id": user.id}


@user.get("/status")
def get_status():

    status = {"mysql": False, "redis": False, "nginx": False}
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
        for conn in psutil.net_connections(kind="tcp"):
            if conn.status == "LISTEN" and conn.laddr.port == 80:
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
    session = request.headers.get("session")
    user_info = redis.get(session)
    if user_info is None:
        raise HTTPException(401, detail="用户未登录")
    user_info = json.loads(user_info)
    return user_info


@user.get("/logout")
def logout(request: Request):
    session = request.headers.get("session")
    redis.delete(session)
    return {"message": "用户已退出"}
