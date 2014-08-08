import random

def rand(a):
    if a < 10 or random.randint(0, 9) > 0:
    	# This will happen in a lot of cases, but it is possible that the other branch is
    	# taken although the probability for this is rather low.
        return 0
    else:
        return 1

def expected_result():
    return [0, 1]