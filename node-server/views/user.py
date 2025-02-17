from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from model import redis
from config import config
import json, logging

router = APIRouter()


class LoginForm(BaseModel):
    id: int
    username: str
    ip: str
    port: int
    session: str


@router.post("/login")  # 根路由
def login(form: LoginForm, request: Request):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.client.host
    if ip != config.center_host:
        raise HTTPException(401, detail="用户未登录")
    user_info = json.dumps(
        {"username": form.username, "id": form.id, "ip": form.ip, "port": form.port}
    )
    redis.set(form.session, user_info, ex=60 * 60 * 24 * 2)
    return {"status": "ok"}


@router.get("/status")
def get_status():
    status = {"mysql": False, "redis": False, "nginx": False}
    # ---------- 检查 Redis 连接 ----------
    try:
        # 使用更具体的异常类型（如 redis.ConnectionError）
        redis.ping()  # 假设 redis_client 是已配置的客户端
        status["redis"] = True
    except redis.ConnectionError as e:
        config.logger.error(f"Redis 连接失败: {e}")
        status["redis"] = False

    return {"data": status}


@router.get("/check_session")
def check_session(request: Request):
    session = request.headers.get("session")
    user_info = redis.get(session)
    if user_info is None:
        raise HTTPException(401, detail="用户未登录")
    return user_info


@router.get("/logout")
def logout(request: Request):
    session = request.headers.get("session")
    redis.delete(session)
    return {"message": "用户已退出"}
