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
	m = max4(a,b,c,d)
	return m

#	if (m < a or m < b or m < c or m < d):
#		return "ERROR"
#	else:
#		return "OK"

#def expected_result():
#	return [ "OK" for i in range(8) ]