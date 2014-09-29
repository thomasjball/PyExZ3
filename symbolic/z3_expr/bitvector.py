from z3 import *
from .expression import Z3Expression

class Z3BitVectorExpression(Z3Expression):
	def __init__(self,N):
		Z3Expression.__init__(self)
		self.N = N

	def _isIntVar(self,v):
		return isinstance(v,BitVecRef)

	def _variable(self,name,solver):
		return BitVec(name,self.N,solver.ctx)

	def _constant(self,v,solver):
		return BitVecVal(v,self.N,solver.ctx)
