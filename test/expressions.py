# Copyright: see copyright.txt

def expressions(in1, in2):
    a = in1
    b = in2 + 47
    c = a * b
    # only solution should be a==1, b==6 (assuming Python actually uses 32-bit integers)
    if c==53: # a > 0 and a < 20 and b < 100 and c == 53:
        d = -1
    else:
        d = 0

    return d

def expected_result():
	return [-1,0]
