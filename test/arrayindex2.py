A = [0, 1, 0, 0, 1, 0, 1]

def arrayindex2(a):

 if a in [ i for i in range(len(A)) if A[i] ]:
   return a
 else:
   return "OTHER"

def expected_result():
  return [ 1,4,6, "OTHER" ]
