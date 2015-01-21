from symbolic.args import *

@symbolic(s="foo")
def emptystr(s):
	if s != '':
		return 0
	else:
		return 1

def expected_result():
	return [0,1]
    
