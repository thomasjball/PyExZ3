from symbolic.args import *

@symbolic(s="foo")
def strcount(s):
    if s.count("x") == 2:
        return 1
    elif s.count("xy") == 1:
        return 2
    else:
        return 0

def expected_result_set():
    return {0, 1, 2}
