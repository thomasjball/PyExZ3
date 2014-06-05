#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
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

import symbolic.z3_wrap as z3_wrap
from symbolic_types import SymbolicType, SymbolicExpression
import logging
import utils
from z3 import *

log = logging.getLogger("se.predicate")

class Predicate:
	"""Predicate is one specific ``if'' encountered during the program execution.
	   """
	def __init__(self, condexpr, result):
		self.expr = condexpr
		self.result = result
		self.sym_variables = {}

	def __eq__(self, other):
		""" Two Predicates are equal iff
		    they have the same statement, same symbolic variables
		    and same result
		"""
		if isinstance(other, Predicate):
			# different result
			if self.result != other.result:
				return False
			# different variables (i.e. another invocation of function for example)
			my_vars = self.expr.getSymVariable()
			other_vars = other.expr.getSymVariable()
			if len(my_vars) != len(other_vars):
				return False
			for i in range(0, len(my_vars)):
				if isinstance(my_vars[i], SymbolicExpression):
					if not my_vars[i].symbolicEq(other_vars[i]):
						return False
				elif my_vars[i] is not other_vars[i]:
					return False
			return True
		else:
			return False

	def __hash__(self):
		return hash(self.expr)

	def negate(self):
		"""Negates the current predicate"""
		assert(self.result is not None)
		self.result = not self.result

	def buildSymPred(self):
		if self.result == None:
			utils.crash("This predicate has an unknown result: %s" % self)

		z3 = z3_wrap._z3
		sym_expr = self.buildZ3Expr()
		if not is_bool(sym_expr):
			# make it boolean
			sym_expr = sym_expr != z3_wrap.int2BitVec(0, self.expr.getBitLength())
		if not self.result:
			sym_expr = Not(sym_expr)
		return (True, sym_expr)

	def __str__(self):
		return str(self.expr) + " (was %s)" % (self.result)

	def __repr__(self):
		return repr(self.expr) + " (was %s)" % (self.result)

	def buildZ3Expr(self):
		if not (isinstance(self.expr,SymbolicType)):
			utils.crash("Unexpected expression %s" % self.expr)
		return z3_wrap.ast2SymExpr(self.expr, self.expr.getBitLength())

		#elif isinstance(stmt, bc.FunctionCall):
		#	if stmt.name == "ord": # We know that our ord does nothing
		#		return self.buildSymExprFromStatement(z3, stmt.params[0], bitlen)


