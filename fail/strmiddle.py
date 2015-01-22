from symbolic.args import *

@symbolic(s="x")
def strmiddle(s):
    x = "A"+s+"C"
    if "B" in x:
        return 0
    else:
        return 1

def expected_result():
	return [0, 1]
    
