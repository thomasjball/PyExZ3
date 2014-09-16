# Copyright: see copyright.txt

import sys
import ast
import logging
import utils
from z3 import *
from .z3_expr.integer import Z3IntegerExpression
from .z3_expr.bitvector import Z3BitVectorExpression

class Z3Wrapper(object):
	def __init__(self):
		self.log = logging.getLogger("se.z3")
		self.solver = Solver()
		self.N = 32
		self.asserts = None
		self.query = None
		self.use_lia = True
		self.z3_expr = None

	def findCounterexample(self, asserts, query):
		"""Tries to find a counterexample to the query while
	  	 asserts remains valid."""
		self.asserts = asserts
		self.query = query
		res = self._findModel()
		if (True):
			print("-- Asserts")
			print(asserts)
			print("-- Query")
			print(query)
			print("-- Result")
			print(res)
		return res

	# private

	def _getModel(self):
		res = {}
		model = self.solver.model()
		for name in self.z3_expr.z3_vars.keys():
			try:
				ce = model.eval(self.z3_expr.z3_vars[name])
				res[name] = ce.as_signed_long()
			except:
				pass
		return res
	
	def _findModel(self):
		# Try QF_LIA first (as it may fairly easily recognize unsat instances)
		if self.use_lia:
			self.solver.push()
			self.z3_expr = Z3IntegerExpression()
			self.z3_expr.toZ3(self.solver,self.asserts,self.query)
			res = self.solver.check()
			#print(self.solver.assertions)
			self.solver.pop()
			if res == unsat:
				return None
		self.N = 32
		self.bound = (1 << 4) - 1
		while self.N <= 64:
			self.solver.push()
			(ret,mismatch) = self._findModel2()
			if (not mismatch):
				break
			self.solver.pop()
			self.N = self.N+8
			if self.N <= 64: print("expanded bit width to "+str(self.N)) 
		#print("Assertions")
		#print(self.solver.assertions())
		if ret == unsat:
			self.log.warning("Z3: UNSAT")
			res = None
		elif ret == unknown:
			self.log.error("Z3: UNKNOWN")
			res = None
		elif not mismatch:
			res = self._getModel()
		else:
			res = None
		if self.N<=64: self.solver.pop()
		return res

	def _findModel2(self):
		self.z3_expr = Z3BitVectorExpression(self.N)
		self.z3_expr.toZ3(self.solver,self.asserts,self.query)
		int_vars = self.z3_expr.getIntVars()
		res = unsat
		while res == unsat and self.bound <= (1 << (self.N-1))-1:
			self.solver.push()
			constraints = self._boundIntegers(int_vars,self.bound)
			self.solver.assert_exprs(constraints)
			res = self.solver.check()
			if res == unsat:
				self.bound = (self.bound << 1)+1
				self.solver.pop()
		if res == sat:
			# Does concolic agree with Z3? If not, it may be due to overflow
			model = self._getModel()
			#print("Match?")
			#print(self.solver.assertions)
			self.solver.pop()
			mismatch = False
			for a in self.asserts:
				eval = self.z3_expr.predToZ3(a,self.solver,model)
				if (not eval):
					mismatch = True
					break
			if (not mismatch):
				mismatch = not (not self.z3_expr.predToZ3(self.query,self.solver,model))
			#print(mismatch)
			return (res,mismatch)
		elif res == unknown:
			self.solver.pop()
		return (res,False)

	def _boundIntegers(self,vars,val):
		bval = BitVecVal(val,self.N,self.solver.ctx)
		bval_neg = BitVecVal(-val-1,self.N,self.solver.ctx)
		return And([ v <= bval for v in vars]+[ bval_neg <= v for v in vars])

