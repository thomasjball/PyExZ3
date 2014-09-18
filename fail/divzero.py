# this one fails because we always start with zero for SymbolicIntegers
# we should have a few seed values to avoid this.

def divzero(in1,in2):
  try:
    if in1 / in2 >= 0:
        return 1
    elif in1 / in2 < 0:
        return 2
    return 0
  except:
    return "DIVZERO"
    
def expected_result():
    return [0,1,2,"DIVZERO"]