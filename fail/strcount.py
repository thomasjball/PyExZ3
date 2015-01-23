from symbolic.args import *

@symbolic(s="x")
def strcount(s):
    if s.count("x") == 5:
        return 1
    elif s.count("xy") == 5:
        return 2
    else:
        return 0

def expected_result():
    return [0, 1, 2]
