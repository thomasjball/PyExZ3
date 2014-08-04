def cseppento1(x,y):
    # based on B2a_IfElse by Lajos Cseppento
    # see: L. Cseppento: Comparison of Symbolic Execution Based Test Generation Tools, B.Sc. Thesis, Budapest University of Technology and Economics, 2013.
    if (x > 0 and y > 0):
        return 1
    elif (x < 0 and y > 0):
        return 2
    elif (x < 0 and y < 0):
        return 3
    elif (x > 0 and y < 0):
        return 4
    elif (x > 0 and y < 0):
        # impossible branch , because the previous is the same
        return -1
    elif (x == 0 or y == 0):
        return 0
    else:
        # impossible branch
        return -2

def expected_result():
    return [0,0,0,1,2,3,4] # should it be [0,1,2,3,4] instead?