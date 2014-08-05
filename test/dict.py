D =  dict({ (101,2), (1,3), (4,9) })

def dict(x):
    # if x in D.keys():
    if x in [ j for j in D.keys() ]:
       return D[x]
    else:
       return "NONE"

def expected_result():
    return [2,3,9,"NONE"]
