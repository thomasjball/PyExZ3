A = [0, 1]

def arrayindex2(a):
 b = False 
 for x in A:
   b = b or (A[x] and (a==x))
 if b:
   return A[a]
 else:
   return "OTHER"

def expected_result():
  return [ 1, "OTHER" ]
