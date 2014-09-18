from math import sqrt

# sqrt is handled concretely, just as with pow (**)

def sqrttest(in1):
    if sqrt(in1) == 0:
        return 1
    elif sqrt(in1) > 0:
        return 2
    return 0

def expected_result():
    return [1,2]