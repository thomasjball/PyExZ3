import random

def rand2(a):
    if random.randint(0, 10) > 0:
        return 0
    else:
        return 1

def expected_result():
    return [0, 1]