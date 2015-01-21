from symbolic.args import *

@symbolic(s="foo")
def bad_eq_str(s):
    x = s + "bar"
    if x == "nobar":
        return 0
    return 1

def expected_result():
	return [0, 1]
    
