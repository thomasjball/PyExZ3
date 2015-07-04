from symbolic.args import *


@symbolic(c=3)
def none(c):
    if c == None:
        return 1
    elif c != None:
        return 0


def expected_result_set():
    return {0}