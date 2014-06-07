# Created by Thomas Ball (2014)
#

def max2(a,b):
	if (a < b):
		return b
	else:
		return a


def max4(a,b,c,d):
	return max2(max2(a,b),max2(c,d))


def maxtest(a,b,c,d):
	return max4(a,b,c,d)


#print maxtest(1,3,9,-1)