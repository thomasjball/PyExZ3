from symbolic.args import *

@symbolic(s="foo")
def strfind(s):
    find_idx = s.find("bar")
    if find_idx == 3:
        return 0
    elif find_idx == -1:
        return 1
    else:
        return 2

def expected_result():
	return [0, 1, 2]
    
