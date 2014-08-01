from adder import *

def multN(xN,yN):
	i = 0
	intermediate = []
	N = len(xN)

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