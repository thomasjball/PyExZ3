def rec_gcd(u,v):
  if (u == v):
    return u

  if (u == 0):
    return v

  if (v == 0):
    return u
 
  if not (u & 1):  # u is even
    if v & 1:      #v is odd
      return rec_gcd(u >> 1, v)
    else:            # both u and v are even
      return rec_gcd(u >> 1, v >> 1) << 1
  else:
    if not (v & 1):  # u is odd, v is even
      return rec_gcd(u, v >> 1)
 
    # reduce larger argument
    if (u > v):
      return rec_gcd((u - v) >> 1, v)

    return rec_gcd((v - u) >> 1, u)

def iter_gcd(u,v):
  # GCD(0,v) == v; GCD(u,0) == u, GCD(0,0) == 0
  if (u == 0): 
    return v
  if (v == 0):
    return u
 
  # Let shift := lg K, where K is the greatest power of 2
  # dividing both u and v.
  shift = 0
  while ((u | v) & 1) == 0:
    u = u >> 1
    v = v >> 1
    shift = shift + 1

  while ((u & 1) == 0):
    u = u >> 1
 
  # From here on, u is always odd.
  while (True):
    # remove all factors of 2 in v -- they are not common
    # note: v is not zero, so while will terminate
    while ((v & 1) == 0):
      v = v >> 1
 
    # Now u and v are both odd. Swap if necessary so u <= v,
    # then set v = v - u (which is even). For bignums, the
    # swapping is just pointer movement, and the subtraction
    # can be done in-place.
    if (u > v):
       u, v = v, u
    v = v - u     # Here v >= u.
    if (v == 0):
      break
 
  # restore common factors of 2
  return u << shift

def gcd(x,y):
  if (x>=0 and y>=0):
     rec_result = rec_gcd(x,y)
     iter_result = iter_gcd(x,y)
     if (rec_result != iter_result):
       return ("ERROR",x,y,rec_result,iter_result)
     else:
       return ("OK",x,y,rec_result)
  else:
     return "PRE"



