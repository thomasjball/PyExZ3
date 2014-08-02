# Copyright: see copyright.txt

# Test if engine explores all paths

def shallow_branches(in1, in2, in3, in4, in5):
    if in1 ==  0:
        return 1

    if in2 ==  0:
        return 3

    if in3 ==  0:
        return 5

    if in4 ==  0:
        return 7

    if in5 ==  0:
        return 9

    return 0

def expected_result():
	return [0, 1, 3, 5, 7, 9]