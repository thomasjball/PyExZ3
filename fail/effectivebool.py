from symbolic.args import *

@symbolic(s="foo", x=1)
def effectivebool(s, x):
	if s:
		return 0
	elif x:
		return 1
	else:
	    return 2

def expected_result():
	return [0,1,2]
    
