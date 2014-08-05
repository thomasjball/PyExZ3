S =  { 1, 3, 9, 12, 15, 19 }

def set(x):
    if x in [ j for j in S]:
       return x
    else:
       return "NONE"

def expected_result():
    return [1,3,9,12,15,19,"NONE"]
