from symbolic.args import *

@symbolic(s="foo")
def testit(s):
	if (s=="bar"):
		return 0
	else:
		return 1

def expected_result():
	return [0,1]
    
