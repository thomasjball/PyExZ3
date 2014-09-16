def powtest(in1):
    if in1*in1 == 0:
        return 1
    elif in1*in1 > 0:
        return 2
    return 0

def expected_result():
    return [1,2]