import multiprocessing
from functools import wraps

# 多进程修饰器
def run_in_process(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        process = multiprocessing.Process(target=func, args=args, kwargs=kwargs)
        process.start()
        return process
    return wrapper