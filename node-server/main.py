import multiprocessing
import time
import threading
from job.job import start_job
from app import start_app


# 监控并重启进程的函数
def monitor_and_restart_processes(process):
    while True:
        if not process.is_alive():
            print(f"[监控] 进程 {process.name} 已退出，正在重启...")
        new_process = multiprocessing.Process(
            target=start_job, name="start_job"
        )
        new_process.start()
        print(f"[监控] 进程 {process.name} 重启成功,pid: {new_process.pid}")
        process = new_process
        time.sleep(1)


if __name__ == "__main__":
    # 初始化子进程列表
    processes = []

    # 创建子进程
    p_job = multiprocessing.Process(target=start_job, name="start_job")
    p_job.start()
    print(f"[主线程] 子进程 {p_job.name} 启动成功, pid: {p_job.pid}")

    # 将监控逻辑放入子线程运行
    monitor_thread = threading.Thread(
        target=monitor_and_restart_processes, args=(p_job,), daemon=True
    )
    monitor_thread.start()

    # 在主线程中运行 FastAPI 应用
    start_app()
