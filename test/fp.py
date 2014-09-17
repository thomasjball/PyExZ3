def fp(a):
	if a % 2 == 0:
		# The next condition basically checks whether a is zero (in a weird way, though).
		if a == int(a / 2):
			return 0
		else:
			return 1
	else:
		return 2

def expected_result():
    return [0, 1, 2]