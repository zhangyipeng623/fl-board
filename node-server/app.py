from fastapi import FastAPI, Request, HTTPException
from views import router_list
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import config
from model import redis

app = FastAPI()  # 创建 api 对象

for router in router_list:  # 注册路由
    app.include_router(router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def check_session(request: Request, call_next):
    not_check_session = [
        "/login",
        "/check_session",
        "/status",
        "/aligned/get_data",
        "/aligned/add",
        "/job/start",
        "/node/metrics",
    ]
    if request.url.path in not_check_session:
        return await call_next(request)
    session = request.headers.get("Authorization")
    user_id = redis.get(session)
    if user_id is None:
        raise HTTPException(401, detail="用户未登录")
    return await call_next(request)


# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.Origins,
    allow_credentials=True,
    allow_methods=config.Allow_methods,  # 允许所有方法 [GET, POST, OPTIONS, etc]
    allow_headers=config.Allow_headers,  # 允许所有请求头
)


def start_app():

    import uvicorn

    uvicorn.run(
        app=config.App,
        host=config.Host,
        port=config.Port,
        reload=config.Reload,
        log_config="./config/uvicorn_config.json",
        reload_excludes=["data/*", "log/*"],
    )
