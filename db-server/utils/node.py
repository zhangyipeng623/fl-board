def get_gpu_info():
    import pynvml

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
        gpu_info[f"{gpu_name}"] = {
            "total": round(memory_info.total / (1024**2), 2),
            "used": round(memory_info.used / (1024**2), 2),
            "free": round(memory_info.free / (1024**2), 2),
            "temperature": temperature,
            "core_frequency": core_frequency,
            "memory_frequency": memory_frequency,
        }

    # 关闭 NVML 库，释放相关资源
    pynvml.nvmlShutdown()

    return gpu_info
