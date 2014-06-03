# Created by Thomas Ball (2014)

def compute(x):
	res = 0
#	res = x + res 
	res = res + x
	res = res + (res << 10)
	res = res ^ (res >> 6)
	res = res + (res << 3)
	res = res ^ (res >> 11)	
	res = res + (res << 15)
	return res
	
def hashval(key):
	hv = compute(key)
	if (hv == 34):
		return 0;
	else:
		return 1;

def expected_result():
	return [0,1]

# test = compute(10010130)