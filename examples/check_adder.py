from adder import *

N = 8

# now prove that adder is equal to bitvector add 

xN = BoolVector("x",N)
yN = BoolVector("y",N)

x_bv = BitVec("x_bv",N)
y_bv = BitVec("y_bv",N)

# need to equate the inputs (Extract(lo,hi,bv)

def eq_bool(bv, i, b):
	return (Extract(i,i,bv) == 1) == b

def eq_bitvec_boolvec(bitvec,boolvec):
	return [ eq_bool(bitvec,i,boolvec[i]) for i in range(bitvec.size())  ]

inputs_equal = eq_bitvec_boolvec(x_bv,xN) + eq_bitvec_boolvec(y_bv,yN)

res,cout = addN(xN,yN,BoolVal(False))

res_bv = x_bv + y_bv

outputs_equal = eq_bitvec_boolvec(res_bv,res)

s = Solver()
s.add(And(inputs_equal))
s.add(Not(And(outputs_equal)))
result = s.check()
print(result)
