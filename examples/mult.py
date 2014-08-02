from adder import *

#  x2 x1 x0
#  y2 y1 y0
  
#  And(x2,y0) And(x1,y0) And(x0,y0)
#  And(x1,y1) And(x0,y1) False
#  And(x0,y2) False      False

def multN(xN,yN):
	i = 0
	intermediate = []
	N = len(xN)

	# create N vectors
	while(i<N):
		false_prefix = [ BoolVal(False) for j in range(i) ]
		suffix = [ And(xN[i],yN[j-i]) for j in range(i,N) ]
		vec = false_prefix + suffix
		intermediate.append(vec)
		i = i + 1

	# now add them up
	res = intermediate[0]
	for j in intermediate[1:]:
		(res,cout) = addN(res,j,BoolVal(False))

	return (res,cout)