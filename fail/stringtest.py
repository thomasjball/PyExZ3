from symbolic.args import *

@symbolic(s=1)
def testit(s):
	if (s=="bar"):
		return 0
	else:
		return 1

def expected_result():
	return [0,1]
    