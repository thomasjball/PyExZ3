def expand(in1, in2):
    if (in1 + in2 >= 1 << 32): 
        return 0
    else:
        return 1

def expected_result():
	return [0,1]
