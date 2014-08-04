def stringtest(x):
    # based on Strings by Lajos Cseppento
    # see: L. Cseppento: Comparison of Symbolic Execution Based Test Generation Tools, B.Sc. Thesis, Budapest University of Technology and Economics, 2013.
   
    if x == "test":
        return 1
    elif x == "TeStInG":
        return 2
    return 0

def expected_result():
    return [0,1,2]