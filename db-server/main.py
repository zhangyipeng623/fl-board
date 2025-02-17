from fastapi import FastAPI, Request,HTTPException
from views import router_list
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import config 
from model import redis
from job.job import start_job
import time,multiprocessing,threading

app = FastAPI() # 创建 api 对象

for router in router_list: # 注册路由
    app.include_router(router) 

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def check_session(request: Request, call_next):
    if request.url.path == "/login" or request.url.path == "/check_session" or request.url.path == "/status" or request.url.path == "/ruler/get" or request.url.path == "/net/get_net_file" :
        return await call_next(request)
    session = request.query_params.get("session")
    user_info = redis.get(session)
    if(user_info is None):
        raise HTTPException(401, detail="用户未登录")
    return await call_next(request)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.Origins,
    allow_credentials=True,
    allow_methods=config.Allow_methods,  # 允许所有方法 [GET, POST, OPTIONS, etc]
    allow_headers=config.Allow_headers,   # 允许所有请求头
)

def start_app():
    import logging
    import uvicorn
    from uvicorn.config import LOGGING_CONFIG
    # 运行fastapi程序
    logging.basicConfig(
            filename=f'./log/app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )

    uvicorn.run(
        app=config.App,
        host=config.Host, 
        port=config.Port, 
        reload=config.Reload,
        log_config="./config/uvicorn_config.json",
        reload_excludes=["data/*","log/*"]
        )

# 监控并重启进程的函数
def monitor_and_restart_processes(processes):
    while True:
        for i, process in enumerate(processes):
            # 判断进程是否已终止
            if not process.is_alive():
                print(f"[监控] 进程 {process.name} 已退出，正在重启...")
                # 重新创建进程
                if process.name == "start_app":
                    new_process = multiprocessing.Process(target=start_app, name="start_app")
                elif process.name == "start_job":
                    new_process = multiprocessing.Process(target=start_job, name="start_job")
                # 确保新进程启动
                new_process.start()
                print(f"[监控] 进程 {process.name} 重启成功,pid: {new_process.pid}")
                # 更新到进程列表
                processes[i] = new_process
        # 稍作等待，避免高频监控浪费资源
        time.sleep(1)


if __name__ == '__main__':
    # 初始化子进程列表
    processes = []

    # 创建子进程
    p_job = multiprocessing.Process(target=start_job, name="start_job")
    processes.append(p_job)

    # 启动子进程
    for process in processes:
        process.start()
        print(f"[主线程] 子进程 {process.name} 启动成功, pid: {process.pid}")

    # 将监控逻辑放入子线程运行
    monitor_thread = threading.Thread(target=monitor_and_restart_processes, args=(processes,), daemon=True)
    monitor_thread.start()

    # 在主线程中运行 FastAPI 应用
    start_app()

