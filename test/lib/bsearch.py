
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
