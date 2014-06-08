def diamond(x,y,z):
	ret = 0
	if (x):
		ret = ret + 1
	if (y):
		ret = ret + 1
	if (z):
		ret = ret + 1
	return ret

def expected_result():
	return [ 0, 1, 1, 1, 2, 2, 2, 3]