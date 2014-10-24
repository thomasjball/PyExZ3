def where_are_the_errors(input):
	k = input // 100
	x = 2
	y = k + 5
	while x < 10:
		x = x + 1
		y = y + 3
	if (3*k + 100) > 43:
		y = y + 1
		# x == 10, y == k+30
		if x - y == 0:
			# unreachable
			return "DIVZERO"
		x = x // (x - y)
	return x

def polyspace(i):
	ret = where_are_the_errors(i)
	return ret
	
def expected_result():
	return [-1,10]