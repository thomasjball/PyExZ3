from math import sqrt

# Test if engine explores all paths


def sqrttest(in1):
    if sqrt(in1) == 0:
        return 1
    elif sqrt(in1) > 0:
        return 2
    return 0

def expected_result():
    return [1,2]