# currently, we don't handle the power operator symbolically,
# so this test is not expected to cover the else branch. The
# initial (concrete) value of x is zero, so we expect only to
# cover the then branch.

def power(x):
	if (x+2) ** 2 == 4:
		return 0
	else:
		return 1

def expected_result():
	return [0]

