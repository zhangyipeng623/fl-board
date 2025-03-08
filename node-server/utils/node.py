import pynvml, subprocess, sys, torch, psutil, time

# 存储上一次的CPU时间数据
last_cpu_times = psutil.cpu_times()
last_check_time = time.time()


def get_gpu_info():

    # 初始化 NVML 库，该库用于与 NVIDIA GPU 进行交互
    pynvml.nvmlInit()

    # 获取系统中可用的 NVIDIA GPU 设备数量
    device_count = pynvml.nvmlDeviceGetCount()

    gpu_info = {}
    for i in range(device_count):
        # 根据索引获取每个 GPU 设备的句柄，后续操作需要通过句柄来访问该 GPU
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)

        # 获取 GPU 的名称，并将其从字节类型解码为字符串类型
        gpu_name = pynvml.nvmlDeviceGetName(handle)

        # 获取 GPU 的内存信息，包括总内存、已使用内存和空闲内存
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)

        # 获取 GPU 的当前温度，第二个参数 0 表示使用默认的温度传感器
        temperature = pynvml.nvmlDeviceGetTemperature(handle, 0)

        # 获取 GPU 当前的核心频率，NVML_CLOCK_GRAPHICS 表示核心频率
        core_frequency = pynvml.nvmlDeviceGetClockInfo(
            handle, pynvml.NVML_CLOCK_GRAPHICS
        )

        # 获取 GPU 当前的显存频率，NVML_CLOCK_MEM 表示显存频率
        memory_frequency = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)

        # 将获取到的 GPU 信息存储在字典中
        gpu_info[f"gpu{i}"] = {
            "name": gpu_name,
            "total": round(float(memory_info.total) / (1024**2), 2),
            "used": round(float(memory_info.used) / (1024**2), 2),
            "free": round(float(memory_info.free) / (1024**2), 2),
            "temperature": temperature,
            "core_frequency": core_frequency,
            "memory_frequency": memory_frequency,
        }

    # 关闭 NVML 库，释放相关资源
    pynvml.nvmlShutdown()

    return gpu_info


def get_cpu_info():
    """获取CPU型号名称"""

    try:
        if sys.platform == "win32":
            # Windows 使用WMIC命令获取CPU名称
            cmd = "wmic cpu get name /value"
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            return output.split("=")[1] if "=" in output else "Unknown CPU"
        elif sys.platform == "darwin":
            # macOS 使用sysctl命令
            cmd = ["sysctl", "-n", "machdep.cpu.brand_string"]
            return subprocess.check_output(cmd).decode().strip()
        elif sys.platform.startswith("linux"):
            # Linux 读取/proc/cpuinfo
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
            return "Unknown CPU"
    except Exception as e:
        pass
    return "Unknown CPU"


def get_metrics_data():
    global last_cpu_times, last_check_time

    # 非阻塞方式获取CPU使用率
    current_cpu_times = psutil.cpu_times()
    current_time = time.time()

    # 计算时间间隔内的CPU使用情况
    time_delta = current_time - last_check_time
    if time_delta > 0:
        # 计算用户态和系统态CPU时间变化
        user_delta = current_cpu_times.user - last_cpu_times.user
        system_delta = current_cpu_times.system - last_cpu_times.system
        idle_delta = current_cpu_times.idle - last_cpu_times.idle

        # 计算总CPU时间变化
        total_delta = user_delta + system_delta + idle_delta

        # 计算CPU使用率
        if total_delta > 0:
            cpu_usage = 100 * (user_delta + system_delta) / total_delta
        else:
            cpu_usage = 0
    else:
        cpu_usage = 0

    # 更新上一次的数据
    last_cpu_times = current_cpu_times
    last_check_time = current_time

    HAS_GPU = torch.cuda.is_available()
    cpu_name = get_cpu_info()
    cpu_freq = round(psutil.cpu_freq().current / 1000, 2)  # 转换为GHz并保留两位小数
    if HAS_GPU:
        gpu_info = get_gpu_info()
    else:
        gpu_info = {}
    return {
        "cpu": {
            "name": cpu_name,
            "cpu_usage": round(cpu_usage, 1),
            "cpu_freq": cpu_freq,
        },
        "gpu_info": gpu_info,
    }
