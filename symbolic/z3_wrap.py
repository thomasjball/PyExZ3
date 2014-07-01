#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
#
# Updated by Thomas Ball (2014)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   -  Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   -  Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#   -  Neither the names of the contributors, nor their associated universities or
#      organizations may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import ast
import logging
import utils
from z3 import *
from .symbolic_types.symbolic_int import SymbolicInteger
from .symbolic_types.symbolic_type import SymbolicType

class Z3Wrapper(object):
	def __init__(self):
		self.log = logging.getLogger("se.z3")
		self.solver = Solver()
		self.z3_vars = {}

	def buildBooleanExpr(self,expr,result):
		sym_expr = self._astToZ3Expr(expr)
		if not is_bool(sym_expr):
			sym_expr = sym_expr != self._int2BitVec(0,32)
		if not result:
			sym_expr = Not(sym_expr)
		return sym_expr

	def findCounterexample(self, z3_asserts, z3_query):
		"""Tries to find a counterexample to the query while
	  	 asserts remains valid."""
		self.solver.push()
		self.solver.assert_exprs(z3_asserts)
		self.solver.assert_exprs(Not(z3_query))
		#print("Assertions")
		#print(_z3.assertions())
		ret = self.solver.check()
		if ret == unsat:
			self.log.warning("Z3: UNSAT")
			print(self.solver.unsat_core())
			self.solver.pop()
			return None
		elif ret == unknown:
			self.log.error("Z3: UNKNOWN")
			self.solver.pop()
			return None
		res = []
		model = self.solver.model()
		#print("Model is ")
		#print(model)
		for name in self.z3_vars.keys():
			try:
				ce = model.eval(self.z3_vars[name])
				res.append((name, ce.as_signed_long()))
			except:
				pass
		self.solver.pop()
		return res

	# private

	def _getIntegerVariable(self,name,bitlen=32):
		if name not in self.z3_vars:
			self.z3_vars[name] = BitVec(name,bitlen, self.solver.ctx)
		else:
			self.log.error("Trying to create a duplicate variable")
		return self.z3_vars[name]

	def _int2BitVec(self,v,length):
		return BitVecVal(v, length, self.solver.ctx)

	def _wrapIf(self,e,bitlen):
		return If(e,self._int2BitVec(1, bitlen),self._int2BitVec(0, bitlen))


	def _astToZ3Expr(self,expr, bitlen=32):
		if isinstance(expr, ast.BinOp):
			z3_l = self._astToZ3Expr(expr.left, bitlen)
			z3_r = self._astToZ3Expr(expr.right, bitlen)

			if isinstance(expr.op, ast.Add):
				return z3_l + z3_r
			elif isinstance(expr.op, ast.Sub):
				return z3_l - z3_r
			elif isinstance(expr.op, ast.Mult):
				return z3_l * z3_r
			elif isinstance(expr.op, ast.LShift):
				return z3_l << z3_r
			elif isinstance(expr.op, ast.RShift):
				return z3_l >> z3_r
			elif isinstance(expr.op, ast.BitXor):
				return z3_l ^ z3_r
			elif isinstance(expr.op, ast.BitOr):
				return z3_l | z3_r
			elif isinstance(expr.op, ast.BitAnd):
				return z3_l & z3_r
			elif isinstance(expr.op, ast.Mod):
				return z3_l % z3_r
			elif isinstance(expr.op, ast.Div):
				return z3_l / z3_r

			# equality gets coerced to integer
			elif isinstance(expr.op, ast.Eq):
				return self._wrapIf(z3_l == z3_r,bitlen)
			elif isinstance(expr.op, ast.NotEq):
				return self._wrapIf(z3_l != z3_r,bitlen)
			elif isinstance(expr.op, ast.Lt):
				return self._wrapIf(z3_l < z3_r,bitlen)
			elif isinstance(expr.op, ast.Gt):
				return self._wrapIf(z3_l > z3_r,bitlen)
			elif isinstance(expr.op, ast.LtE):
				return self._wrapIf(z3_l <= z3_r,bitlen)
			elif isinstance(expr.op, ast.GtE):
				return self._wrapIf(z3_l >= z3_r,bitlen)

			else:
				utils.crash("Unknown BinOp during conversion from ast to Z3 (expressions): %s" % expr.op)

		elif isinstance(expr, SymbolicInteger):
			if expr.isVariable():
				return self._getIntegerVariable(expr.name,bitlen)
			else:
				return self._astToZ3Expr(expr.expr,bitlen)

		elif isinstance(expr, SymbolicType):
			return self._astToZ3Expr(expr.expr,bitlen)

		elif isinstance(expr, int) or isinstance(expr, long):
			return self._int2BitVec(expr, bitlen)

		else:
			utils.crash("Unknown node during conversion from ast to Z3 (expressions): %s" % expr)

