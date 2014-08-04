def loop(in1,in2):
    if in1 > in2:
        i = 0
        while i < in1 and False:
            i = i+1
        return 1
    else:
        return 0
        
def expected_result():
    return [0,1,1]