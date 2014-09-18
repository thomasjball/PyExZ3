A = [0, 1, 0, 0, 1, 0, 1]

def arrayindex2(i):

 if i in [ j for j in range(len(A)) if A[j] ]:
   return i
 else:
   return "OTHER"

def expected_result():
  return [ 1,4,6, "OTHER" ]
