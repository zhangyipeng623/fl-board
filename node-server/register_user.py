from config import config
import requests
import platform
import subprocess
import sys


def get_system_info():
    """获取操作系统名称和版本号"""
    system = platform.system()
    if system == "Darwin":
        # macOS 获取更友好的版本名称（如 'macOS 13.5'）
        version = platform.mac_ver()[0]
        version_parts = version.split(".")[:2]
        return "macOS", ".".join(version_parts)
    elif system == "Windows":
        # Windows 获取详细版本号（如 '10.0'）
        version = platform.version()
        version_parts = version.split(".")[:2]  # 取前两个版本号
        return "Windows", ".".join(version_parts)
    elif system == "Linux":
        # Linux 获取发行版名称（如 'Ubuntu 22.04.3 LTS'）
        try:
            import distro

            return "Linux", distro.name(pretty=True)
        except ImportError:
            return "Linux", platform.release()
    return system, platform.release()


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


def get_gpu_info():
    """获取GPU型号名称"""
    try:
        if sys.platform == "win32":
            # Windows 使用WMIC命令获取第一个GPU名称
            cmd = "wmic path win32_VideoController get name /value"
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            return output.split("=")[1] if "=" in output else "Unknown GPU"
        elif sys.platform == "darwin":
            # macOS 使用system_profiler命令
            cmd = ["system_profiler", "SPDisplaysDataType"]
            output = subprocess.check_output(cmd).decode()
            return output.split("Chipset Model: ")[1].split("\n")[0].strip()
        elif sys.platform.startswith("linux"):
            # Linux 优先尝试nvidia-smi，否则使用lspci
            try:
                output = (
                    subprocess.check_output(
                        ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]
                    )
                    .decode()
                    .strip()
                )
                return output.split("\n")[0]
            except:
                output = subprocess.check_output(["lspci", "-nnk"]).decode()
                for line in output.split("\n"):
                    if "VGA" in line or "3D" in line:
                        return line.split(": ")[-1].split(" (")[0]
            return "Unknown GPU"
    except Exception as e:
        pass
    return "Unknown GPU"


if __name__ == "__main__":
    system_name, system_version = get_system_info()
    cpu_name = get_cpu_info()
    gpu_name = get_gpu_info()
    print(f"目前设置center:{config.center_host}:{config.center_port}")
    print(f"目前设置local:{config.Host}:{config.Port}")
    # 打印结果
    print(f"操作系统: {system_name}:{system_version}")
    print(f"CPU型号: {cpu_name}")
    print(f"GPU型号: {gpu_name}")

    print("是否正确？(y/n)")

    is_correct = input()
    if is_correct == "n":
        print("请重新设置")
        exit()

    print("请输入注册的用户名:")
    username = input()
    print("请输入注册的密码:")
    password = input()
    print("请重复输入密码:")
    password2 = input()

    if password != password2:
        print("两次密码不一致")
        exit()

    register_info = {
        "username": username,
        "password": password,
        "ip": config.Host,
        "port": config.Port,
        "system": system_name + ":" + system_version,
        "cpu": cpu_name,
        "gpu": gpu_name,
    }

    res = requests.post(
        f"http://{config.center_host}:{config.center_port}/register", json=register_info
    )
    if res.status_code == 200:
        print("注册成功")
    else:
        print(f"注册失败,{res.text}")
