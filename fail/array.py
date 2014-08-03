ARRAY = [0, 1]

def array(a):
  if ARRAY[a]:
    return ARRAY[a]
  else:
    return "OTHER"

def expected_result():
  return [ 1, "OTHER" ]
