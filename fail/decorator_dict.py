from symbolic.args import *

@symbolic(d=dict([(42,6)]))
def decorator_dict(d):
	if d[42] == 6:
		return 0
	else:
		return 1

def expected_result():
	return [0]