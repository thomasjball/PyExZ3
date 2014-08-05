from lib.bsearch import *

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

