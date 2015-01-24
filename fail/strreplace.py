from symbolic.args import *


@symbolic(s="foo")
def strreplace(s):
    if "faa" == s.replace("o", "a"):
        return 0
    else:
        return 1


def expected_result():
    return [0, 1]
    
