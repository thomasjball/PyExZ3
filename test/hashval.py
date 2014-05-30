def hash(in1):
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
