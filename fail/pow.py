# this one fails because we treat the operator ** concretely rather than symbolically
# so that the concrete value 0**2 is substituted in place of x**2.
# As a result, we never get to calling the theorem prover

def pow(x):
  if 4 == x**2:
    return "POW"
  else:
    return "OTHER"

def expected_result():
  return [ "OTHER", "POW" ]
