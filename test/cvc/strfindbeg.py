from symbolic.args import *

@symbolic(s="foo")
def strfindbeg(s):
    find_idx = s.find("bar", 1)
    if find_idx == 3:
        return 0
    elif find_idx == -1:
        return 1
    else:
        return 2

def expected_result():
    return [0, 1, 2]
