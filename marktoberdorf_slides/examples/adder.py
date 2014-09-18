from z3 import *

def add1(x0,y0,c0):
	return (simplify(Xor(Xor(x0,y0),c0)), 
                simplify(Or(And(x0,y0),And(x0,c0),And(y0,c0))))

def addN(xN,yN,cin):
	res = []
	cout = cin
	for (x,y) in zip(xN,yN):
		(new_res,cout) = add1(x,y,cout)
		res.append(new_res)
	return (res,cout)

