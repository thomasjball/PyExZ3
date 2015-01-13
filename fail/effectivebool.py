"""Tests strings and integers used as a branch condition. The
interpreter calls the bool constructor with the contents of the branch
condition passed in as the argument. If a __bool__ function does not
exist, __len__ is called and compared to zero."""
from symbolic.args import *

@symbolic(string="foo", num=1)
def effectivebool(string, num):
    if string:
        return 0
    elif num:
        return 1
    else:
        return 2

def expected_result():
    return [0, 1, 2]
