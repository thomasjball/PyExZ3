import sys

def bignum(a):
  if a == sys.maxsize:
    return "bv"
  if a == sys.maxsize+1:
    return "bignum"
  return "other"

def expected_result():
  return [ "other", "bv", "bignum" ]
