from z3 import *

N = 13
zerosN = [BoolVal(False)] * N

def multcell(a,b,c,s):
	# I have to admit it is based on http://www.xilinx.com/univ/teaching_materials/dsp_primer/sample/lecture_notes/FPGAArithmetic_mult.pdf , slide 3.
	y = And(a,b)
	(sout,cout) = add1(s,y,c)
	return (cout,sout)
	
def multN(xN,yN):
	# to sum up the columns
	sums = zerosN
	
	for row in range(N):
		b = yN[row] # yN is not shifted
		# initialise carry to 0
		c = BoolVal(False)
		
		for col in range(row,N): # note that col<row cells are skipped!
			# collect the inputs
			
			# xN is shifted in each row
			a = xN[col-row]
			# sum up the columns
			s = sums[col]
			
			# make a multiplication cell
			(co,so) = multcell(a,b,c,s)
			
			# outputs
			c = co
			sums[col] = so
	return sums
	
def add1(x0,y0,c0):
	return (simplify(Xor(Xor(x0,y0),c0)) , simplify(Or(And(x0,y0),And(x0,c0),And(y0,c0))))