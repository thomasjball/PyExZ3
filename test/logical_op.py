# Copyright: see copyright.txt

def logical_op(in1, in2):
    if (in1 & in2) == 1:
        if (in1 & in2) == 7:
            return 1
        else:
            return 2
    else:
        return 3

    return 0

def expected_result():
	return [2,3]