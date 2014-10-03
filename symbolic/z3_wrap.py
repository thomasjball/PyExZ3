# Copyright: see copyright.txt

import sys
import ast

from z3 import *
from .z3_expr.integer import Z3Integer
from .z3_expr.bitvector import Z3BitVector

class Z3Wrapper(object):
	def __init__(self):
		self.N = 32
		self.asserts = None
		self.query = None
		self.use_lia = True
		self.z3_expr = None

	def findCounterexample(self, asserts, query):
		"""Tries to find a counterexample to the query while
	  	 asserts remains valid."""
		self.solver = Solver()
		self.query = query
		self.asserts = self._coneOfInfluence(asserts,query)
		res = self._findModel()
		if (False):
			print("-- Query")
			print(self.query)
			print("-- Asserts")
			print(asserts)
			print("-- Cone")
			print(self.asserts)
			print("-- Result")
			print(res)
		return res

	# private

	# this is very inefficient
	def _coneOfInfluence(self,asserts,query):
		cone = []
		cone_vars = set(query.getVars())
		ws = [ a for a in asserts if len(set(a.getVars()) & cone_vars) > 0 ]
		remaining = [ a for a in asserts if a not in ws ]
		while len(ws) > 0:
			a = ws.pop()
			a_vars = set(a.getVars())
			cone_vars = cone_vars.union(a_vars)
			cone.append(a)
			new_ws = [ a for a in remaining if len(set(a.getVars()) & cone_vars) > 0 ]
			remaining = [ a for a in remaining if a not in new_ws ]
			ws = ws + new_ws
		return cone

	def _findModel(self):
		# Try QF_LIA first (as it may fairly easily recognize unsat instances)
		if self.use_lia:
			self.solver.push()
			self.z3_expr = Z3Integer()
			self.z3_expr.toZ3(self.solver,self.asserts,self.query)
			res = self.solver.check()
			#print(self.solver.assertions)
			self.solver.pop()
			if res == unsat:
				return None

		# unsound check for unsat at 32 bits

		self.N = 32
		self.solver.push()
		self._setAssertsQuery()
		ret = self.solver.check()
		self.solver.pop()
		if ret == unsat:
			return None

		# If we were interested in really proving UNSAT,
		# we would need to generate an overapproximation
		# of the formula from the proof of UNSAT, as in
		# @incollection{
		# year={2007},
		# booktitle={Tools and Algorithms for the Construction and Analysis of Systems},
		# volume={4424},
		# series={Lecture Notes in Computer Science},
		# title={Deciding Bit-Vector Arithmetic with Abstraction},
		# author={Bryant, RandalE. and Kroening, Daniel and Ouaknine, Joël and Seshia, SanjitA. and Strichman, Ofer and Brady, Bryan},
		# pages={358-372},
		# }

		# now, go for SAT with bounds
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
			res = None
		elif ret == unknown:
			res = None
		elif not mismatch:
			res = self._getModel()
		else:
			res = None
		if self.N<=64: self.solver.pop()
		return res

	def _setAssertsQuery(self):
		self.z3_expr = Z3BitVector(self.N)
		self.z3_expr.toZ3(self.solver,self.asserts,self.query)

	def _findModel2(self):
		self._setAssertsQuery()
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
	
	def _boundIntegers(self,vars,val):
		bval = BitVecVal(val,self.N,self.solver.ctx)
		bval_neg = BitVecVal(-val-1,self.N,self.solver.ctx)
		return And([ v <= bval for v in vars]+[ bval_neg <= v for v in vars])

