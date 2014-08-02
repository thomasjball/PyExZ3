def tuplelt(a, b):
  a0, a1 = a
  b0, b1 = b

  if a0 < b0:
    return True
  elif a1 < b1:
    return True
  return False

def tuplecmp(a0, a1, b0, b1):
  return tuplelt((a0, a1), (b0, b1))

def expected_result():
  return [True, True, False]
