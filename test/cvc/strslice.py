from symbolic.args import *

@symbolic(s="foo")
def strslice(s):
    if '\\' not in s and s[0:2] == "//":
        return 0
    return 1

def expected_result_set():
    return {0, 1}
