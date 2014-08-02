def complex(x,y):
  if (y >= 1<<32):
    h = hash(y)
    print(h)
    if (x == h):
      if (y == 1<<32 + 203):
        return 0
      else:
        return 1
    else:
      return 2

def expected_results():
	return [0,1,2]


