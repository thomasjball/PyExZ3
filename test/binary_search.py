def bsearch(a,k):
	lo, hi = 0, len(a)-1
	while(lo <= hi):
		mid = (lo+hi) >> 1
		if (a[mid] == k):
			return mid
		elif (a[mid] < k):
			lo = mid+1
		else:
			hi = mid-1
	return -1

array = [ 0, 4, 6, 95, 430, 4944, 119101 ]

def binary_search(k):
	i = bsearch(array,k)
	if(i>=0):
		if (not array[i]==k):
			return "ERROR"
		else:
			return str(k)
	else:
		if (k in array):
			return "ERROR"
		else:
			return "NOT_FOUND"

def expected_result(): 
	return [str(i) for i in array] + [ "NOT_FOUND" for i in range(len(array)+1) ]