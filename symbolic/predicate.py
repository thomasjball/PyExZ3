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
import bytecode_opcodes as bc
from symbolic_types import SymbolicExpression
import logging
import utils
from z3 import *

log = logging.getLogger("se.predicate")

class Predicate:
	"""Predicate is one specific ``if'' encountered during the program execution.
	   """

	def __init__(self, stmt, result):
		"""stmt is statement under consideration
			next_opcode_id is used to determine branch taken
			"""
		self.stmt = stmt
		self.result = result
		self.sym_variables = {}

	def __eq__(self, other):
		""" Two Predicates are equal iff
		    they have the same statement, same symbolic variables
		    and same result
		"""
		if isinstance(other, Predicate):
			# it is a different bytecode instruction
			if self.stmt.opcode_id != other.stmt.opcode_id:
				return False
			# different result
			if self.result != other.result:
				return False
			# different variables (i.e. another invocation of function for example)
			my_vars = self.stmt.getSymbolicVariables()
			other_vars = other.stmt.getSymbolicVariables()
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
		return hash(self.stmt.opcode_id)

	def negate(self):
		"""Negates the current predicate"""
		assert(self.result is not None)
		self.result = not self.result

	def needsSolver(self):
		if isinstance(self.stmt.condition, bc.FunctionCall) and self.stmt.condition.name[-7:] == "has_key":
			return False
		else:
			return True

	def buildSymPred(self, context):
		if self.stmt == None:
			utils.crash("Predicate without statement")
		self.stmt.refreshRef(context)
		if self.result == None:
			utils.crash("This predicate has an unknown result: %s" % self)

		z3 = z3_wrap._z3

		if self.needsSolver():
			c = self.stmt.condition
			bitlen = c.getBitLength()
			sym_expr = self.buildSymExprFromStatement(z3, c, bitlen)
			if not is_bool(sym_expr):
				# make it boolean, stp does not like things like (a & 1) used as boolean expressions
				sym_expr = sym_expr != z3_wrap.int2BitVec(0, bitlen)
			if not self.result:
				sym_expr = Not(sym_expr)
			return (True, sym_expr)

		log.error("Cannot fix predicate %s, skipping" % self)
		return (False, None)

	def __str__(self):
		return str(self.stmt) + " (was %s)" % (self.result)

	def __repr__(self):
		return repr(self.stmt) + " (was %s)" % (self.result)

	def buildSymExprFromStatement(self, z3, stmt, bitlen):
		"""This function is recursive"""
		if isinstance(stmt, bc.BinaryOperator):
			SymLeft = self.buildSymExprFromStatement(z3, stmt.left, bitlen)
			SymRight = self.buildSymExprFromStatement(z3, stmt.right, bitlen)
			if stmt.name == "==":
				return SymLeft == SymRight
			if stmt.name == "&":
				return SymLeft & SymRight
			if stmt.name == "<":
				return SymLeft < SymRight
			if stmt.name == ">":
				return SymLeft > SymRight
			if stmt.name == "<=":
				return SymLeft <= SymRight
			if stmt.name == ">=":
				return SymLeft >= SymRight
			if stmt.name == "!=":
				return SymLeft != SymRight
			else:
				utils.crash("Cannot build symbolic expression for unknown operator %s" % stmt.name)
		elif isinstance(stmt, bc.Attribute) or isinstance(stmt, bc.LocalReference) or isinstance(stmt, bc.GlobalReference) or isinstance(stmt, bc.Subscr):
			if stmt.isSymbolic():
				sym_var = stmt.reference # could be an expression
				sym_vars = sym_var.getSymVariable()
				for name, var, sym_var in sym_vars:
					self.sym_variables[name] = (var, sym_var)
				if isinstance(sym_var, SymbolicExpression):
					return z3_wrap.ast2SymExpr(sym_var.expr, sym_var.getBitLength())
				else:
					return sym_vars[0][2]
			else:
				v = long(stmt.value) # Try to get an int
				return z3_wrap.int2BitVec(v, bitlen)
		elif isinstance(stmt, bc.FunctionCall):
			if stmt.name == "ord": # We know that our ord does nothing
				return self.buildSymExprFromStatement(z3, stmt.params[0], bitlen)
			elif stmt.name[-7:] == "has_key":
				utils.crash("Cannot build symbolic expression for has_key call %s" % stmt.name)
			else:
				utils.crash("Cannot build symbolic expression for unknown function %s" % stmt.name)
		elif isinstance(stmt, bc.ConstantValue):
			v = long(stmt.reference)
			return z3_wrap.int2BitVec(v, bitlen)
		elif isinstance(stmt, bc.UnaryOperator):
			if stmt.name == "not":
				e = self.buildSymExprFromStatement(z3, stmt.expr, bitlen)
				if is_bool(e):
					return Not(e)
				else:
					# make it boolean, stp does not like things like (a & 1) used as boolean expressions
					# so we transform the whole not expression to (a & 1) == 0
					return e != z3.int2BitVec(0, bitlen)
			else:
				utils.crash("Unkown unary operator %s" % stmt.name)
		else:
			utils.crash("Cannot build symbolic expression for unknown class %s" % stmt.__class__.__name__)

