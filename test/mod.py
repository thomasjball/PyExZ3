def mod(x,y):
	if 0 < y < 10 and x % (y+1) == 3:
		return 0
	else:
		return 1

def expected_result():
	return [0,1,1,1]

