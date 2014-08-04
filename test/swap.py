def swap(in1,in2):
    if in1 > in2:
        # swap in1 and in2
        in1 = in1 ^ in2;
        in2 = in1 ^ in2;
        in1 = in1 ^ in2;
        
        if in1 > in2:
            # impossible
            return 1
        else:
            return 2
    else:
        return 0
        
def expected_result():
    return [0,2]