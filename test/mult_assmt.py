
def mult_assmt(in1,in2,in3):
    v = in1
    if v == in2:
        if in3 > 0:
            v = v + 1
        
        if v != in2:
            return 1
        else:
            return 2
    
    return 0

def expected_result():
    return [0,1,2]