from job.job import start_job
import time, multiprocessing, threading
from app import start_app


# 监控并重启进程的函数
def monitor_and_restart_processes(processes):
    while True:
        for i, process in enumerate(processes):
            # 判断进程是否已终止
            if not process.is_alive():
                print(f"[监控] 进程 {process.name} 已退出，正在重启...")
                # 重新创建进程
                if process.name == "start_app":
                    new_process = multiprocessing.Process(
                        target=start_app, name="start_app"
                    )
                elif process.name == "start_job":
                    new_process = multiprocessing.Process(
                        target=start_job, name="start_job"
                    )
                # 确保新进程启动
                new_process.start()
                print(f"[监控] 进程 {process.name} 重启成功,pid: {new_process.pid}")
                # 更新到进程列表
                processes[i] = new_process
        # 稍作等待，避免高频监控浪费资源
        time.sleep(1)


if __name__ == "__main__":
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
    monitor_thread = threading.Thread(
        target=monitor_and_restart_processes, args=(processes,), daemon=True
    )
    monitor_thread.start()

    # 在主线程中运行 FastAPI 应用
    start_app()
