def power2(x):
	b = x * x;
	if b > 0:
		return 0
	elif b == 0:
		return 1
	else:
		# This path is not possible if it is guaranteed that overflows do not occur.
		return 2

def expected_result():
	return [0, 1]

