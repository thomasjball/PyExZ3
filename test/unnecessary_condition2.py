def unnecessary_condition2(in1,in2):
    if in1 > in2:
        # unnec always false
        unnec = in1 < 5 and False # this is a branching point because of (in1 < 5)
        if unnec: # this is not a real branching point
            return 2
        return 1
    else:
        return 0
        
def expected_result():
    return [0,1,1]