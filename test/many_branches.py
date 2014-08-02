# Copyright: see copyright.txt

# Test if engine explores all paths

def many_branches(in1, in2, in3):
    if in1 == 0:
        if in2 == 5:
            if in3 == 10:
                return 1
            else:
                return 2
        else:
            if in3 <= 3:
                return 3
            else:
                return 4
    else:
        if in1 == 1:
            if in2 == 7:
                return 5
            else:
                return 6
        else:
            if in2 == 9:
                return 7
            else:
                return 8

    return 0

def expected_result():
	return [1, 2, 3, 4, 5, 6, 7, 8]