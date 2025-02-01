from fastapi import FastAPI, Request,HTTPException
from views import router_list
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import config 
from model import redis

app = FastAPI() # 创建 api 对象

for router in router_list: # 注册路由
    app.include_router(router) 

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def check_session(request: Request, call_next):
    if request.url.path == "/login" or request.url.path == "/check_session" or request.url.path == "/status" or request.url.path == "/aligned/get_data":
        return await call_next(request)
    session = request.query_params.get("session")
    user_id = redis.get(session)
    if(user_id is None):
        raise HTTPException(status_code=401, detail="用户未登录")
    return await call_next(request)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.Origins,
    allow_credentials=True,
    allow_methods=config.Allow_methods,  # 允许所有方法 [GET, POST, OPTIONS, etc]
    allow_headers=config.Allow_headers,   # 允许所有请求头
)




if __name__ == '__main__':
    import uvicorn
    # 运行fastapi程序
    uvicorn.run(
        app=config.App,
        host=config.Host, 
        port=config.Port, 
        reload=config.Reload
        )
