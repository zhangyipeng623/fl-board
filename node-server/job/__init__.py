# 显式声明包版本和模块
__version__ = "1.0"
__all__ = ["start_job", "start"]  # 明确导出符号

# 延迟导入防止循环依赖
from .job import start_job
from .node_server import start
