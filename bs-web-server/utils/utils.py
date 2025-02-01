def add(*args):
    return round(sum(args),2)

def sub(*args):
    #  减法
    return round(args[0] - sum(args[1:]),2)

def mul(*args):
    #  乘法 所有数据相乘
    result = 1  
    for i in args:
        result *= i
    return round(result,2)

def div(*args):
    #  除法 所有数据相除
    result = args[0]
    for i in args[1:]:
        result /= i
    return round(result,2)