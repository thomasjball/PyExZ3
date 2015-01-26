from symbolic.args import *

@symbolic(s="foo")
def strsubstring(s):
    """Test case for Python slicing, negative indices and steps are not currently tested."""
    if s[2:] == "obar":
        return 0
    elif s[:2] == "bb":
        return 1
    elif s[1:3] == "bb":
        return 2
    else:
        return 3

def expected_result():
    return [0, 1, 2, 3]
