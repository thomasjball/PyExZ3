from symbolic.args import *

@concrete(a=1,b=2)
@symbolic(c=3)
def decorator(a,b,c):
	if a+b+c == 6:
		return 0
	else:
		return 1

def expected_result():
	return [0,1]