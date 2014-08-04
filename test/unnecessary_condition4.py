def unnecessary_condition4(in1):
    v = op(in1)

    if in1 > 0:
        # in1 > 0
        return v + 10
    else:
        return v + 20
        
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