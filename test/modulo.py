def modulo(in1):
    if in1 % 3 != 0:
        return 1
    elif in1 % 5 != 0:
        return 2
    return 0
    
def expected_result():
    return [0,1,2]