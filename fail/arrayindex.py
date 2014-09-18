A = [0, 1]

# the index operation A[i] uses the underlying runtime representation
# of the Python int, so we have no way of capturing this "conditional
# through lookup" operation via inheritance from int, as done with 
# SymbolicInteger

# see test\arrayindex2.py for the rewriting we would need to do
# to make the lookup explicit (greatly expanding the search space)

def arrayindex(i):
  if A[i]:
    return A[i]
  else:
    return "OTHER"

def expected_result():
  return [ 1, "OTHER" ]
