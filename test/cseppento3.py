def cseppento3(x):
    # based on B3c_DoWhile by Lajos Cseppento
    # see: L. Cseppento: Comparison of Symbolic Execution Based Test Generation Tools, B.Sc. Thesis, Budapest University of Technology and Economics, 2013.
   
# Sum of the positive integers <= min (x, 100)
# 1+2+4+5+7+8+...[+98+100]
    i = 1
    sum = 0
    while (i<=x):
        i = i + 1
        if (i % 3 == 0):
            continue
        if (i > 100):
            break
        sum = sum + i
    return sum

#def expected_result():
#    return []
    