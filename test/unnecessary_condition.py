def unnecessary_condition(in1,in2):
    if in1 > in2:
        unnec = in1 < in2 and False
        if unnec:
            return 2
        return 1
    else:
        return 0
        
def expected_result():
    return [0,1]