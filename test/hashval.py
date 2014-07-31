# Created by Thomas Ball (2014)

def compute(x):
	res = x
	res = res + (res << 10)
	res = res ^ (res >> 6)
	return res
	
def hashval(key):
	hv = compute(key)
	if (hv == key + 1):
		return 0
	else:
		return 1

def expected_result():
	return [1]

