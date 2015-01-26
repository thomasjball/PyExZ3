from symbolic.args import *

@symbolic(s="foobar")
def strindex(s):
    """Test case does not currently test negative indexes."""
    if s[4] == 'Q':
        return 0
    else:
        return 1

def expected_result():
    return [0, 1]
