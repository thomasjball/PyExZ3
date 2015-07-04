from symbolic.args import *

@symbolic(s="foo")
def strstartswith(s):
    if s.startswith('abc'):
        return 0
    return 1

def expected_result_set():
    return {0, 1}