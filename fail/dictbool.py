from symbolic.args import *

@symbolic(d={})
def dictbool(d):
    x = d or {}
    if x == {}:
        return 0
    return 1

def expected_result():
	return [0, 1]
    
