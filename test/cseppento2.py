def cseppento2(a,b):
    # based on B2c_NonLinear by Lajos Cseppento
    # see: L. Cseppento: Comparison of Symbolic Execution Based Test Generation Tools, B.Sc. Thesis, Budapest University of Technology and Economics, 2013.
    if (2 * a * a - 5 * a + 3 == 0 and 2 * b * b - 5 * b + 3 == 0 and a != b):
        return 1
    else:
        return 2

def expected_result():
    return [2,2,2] # should it be [2] ?