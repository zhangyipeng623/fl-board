import threading
from functools import wraps


# 多线程修饰器
def run_in_thread(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = False
        thread.start()
        return thread

    return wrapper


def add(*args):
    return round(sum(args), 2)


def sub(*args):
    #  减法
    return round(args[0] - sum(args[1:]), 2)


def mul(*args):
    #  乘法 所有数据相乘
    result = 1
    for i in args:
        result *= i
    return round(result, 2)


def div(*args):
    #  除法 所有数据相除
    result = args[0]
    for i in args[1:]:
        result /= i
    return round(result, 2)
