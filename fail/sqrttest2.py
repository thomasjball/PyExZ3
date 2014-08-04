from math import sqrt

def sqrttest2(in1,lim):
    if sqrt(in1) == lim:
        return 1
    elif sqrt(in1) > lim:
        return 2
    return 0

def expected_result():
    return [0,1,2]