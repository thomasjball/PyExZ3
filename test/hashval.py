# Created by Thomas Ball (2014)

def hashval(in1):
	hash = 0
	hash = hash + in1
	hash = hash + (hash << 10)
	hash = hash ^ (hash >> 6)
	hash = hash + (hash << 3)
	hash = hash ^ (hash >> 11)	
	hash = hash + (hash << 15)
	if (hash == 34):
		return 0;
	else:
		return 1;

def expected_result():
	return [0,1]