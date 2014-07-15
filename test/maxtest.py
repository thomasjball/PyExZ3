# Created by Thomas Ball (2014)
#

def max2(s,t):
	if (s < t):
		return t
	else:
		return s


def max4(x,y,x2,y2):
	return max2(max2(x,y),max2(x2,y2))


def maxtest(a,b,c,d):
	return max4(a,b,c,d)


#print maxtest(1,3,9,-1)