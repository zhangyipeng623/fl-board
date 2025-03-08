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


def map_dtype_to_simple_type(dtype):
    """将数据类型映射为简单类型

    Args:
        dtype: 输入的数据类型

    Returns:
        str: 映射后的简单类型名称，可能的返回值包括:
            - 'int': 整数类型
            - 'float': 浮点数类型 
            - 'str': 字符串类型
            - 'array': 数组类型
            - 'list': 列表类型
    """
    dtype_str = str(dtype)
    if 'int' in dtype_str:
        return 'int'
    elif 'float' in dtype_str:
        return 'float'
    elif 'object' in dtype_str or 'O' == dtype_str:
        return 'str'
    elif 'array' in dtype_str:
        return 'array'
    elif 'list' in dtype_str:
        return 'list'
    else:
        return 'str'  # 默认返回str类型


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
