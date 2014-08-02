# Copyright: see copyright.txt

# Test if engine explores all paths

def elseif(in1):
    if in1 ==  0:
        return 0
    elif in1 == 1:
        return 1
    elif in1 == 2:
        return 2
    elif in1 == 3:
        return 3
    elif in1 == 4:
        return 4
    elif in1 == 5:
        return 5
    elif in1 == 6:
        return 6
    elif in1 == 7:
        return 7
    elif in1 == 8:
        return 8
    else:
        return 9
    return 10

def expected_result():
	return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]