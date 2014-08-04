def unnecessary_condition3(in1):
    if in1 > 0:
        # in1 > 0
        return op(in1) + 10
    else:
        return op(in1) + 20
        
def op(in1):
    if in1 < -10:
        return 1
    if in1 < -5:
        return 2
    if in1 < -3:
        return 3
    if in1 < 0:
        return 4
        
    return 0
    
def expected_result():
    return [10,20,21,22,23,24]