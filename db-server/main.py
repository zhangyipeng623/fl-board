from fastapi import FastAPI
from views import router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import config 

app = FastAPI() # 创建 api 对象
app.include_router(router) # 注册路由
app.mount("/static", StaticFiles(directory="static"), name="static")


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
