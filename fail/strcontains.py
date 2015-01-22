from symbolic.args import *

@symbolic(s="foo")
def strcontains(s):
	if "bar" in s:
		return 0
	else:
		return 1

def expected_result():
	return [0,1]
    
