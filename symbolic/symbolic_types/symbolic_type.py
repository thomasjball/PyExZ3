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
import sys

def correct(value, bits, signed):
    base = 1 << bits
    value %= base
    return value - base if signed and value.bit_length() == bits else value

char, word, dword, qword, byte, sword, sdword, sqword = (
    lambda v: correct(v, 8, True), lambda v: correct(v, 16, True),
    lambda v: correct(v, 32, True), lambda v: correct(v, 64, True),
    lambda v: correct(v, 8, False), lambda v: correct(v, 16, False),
    lambda v: correct(v, 32, False), lambda v: correct(v, 64, False))

# the base class for representing any expression that depends on a symbolic input
# it also tracks the corresponding concrete value for the expression (aka concolic execution)

#   MISSING: Mod | Pow  | FloorDiv, and much more...

class SymbolicType:
	def __init__(self, name):
		self.name = name
		self.concrete_value = None

	def isSymbolic(self):
		return True

	def getBitLength(self):
		raise NotImplementedError

	def getExprConcr(self):
		return (self, self.getConcrValue())

	def __nonzero__(self):
		return bool(self.getConcrValue())

	def __ord__(self):
		return self

	def __hash__(self):
		return hash(self.getConcrValue())

	def __cmp__(self, other):
		return NotImplemented

	def __eq__(self, other):
		if isinstance(other, type(None)):
			return False
		else:
			return self._do_bin_op(other, lambda x, y: x == y, ast.Eq)

	def __ne__(self, other):
		if isinstance(other, type(None)):
			return True
		else:
			return self._do_bin_op(other, lambda x, y: x != y, ast.NotEq)

	def __lt__(self, other):
		return self._do_bin_op(other, lambda x, y: x < y, ast.Lt)

	def __le__(self, other):
		return self._do_bin_op(other, lambda x, y: x <= y, ast.LtE)

	def __gt__(self, other):
		return self._do_bin_op(other, lambda x, y: x > y, ast.Gt)

	def __ge__(self, other):
		return self._do_bin_op(other, lambda x, y: x >= y, ast.GtE)

	# compute both the symbolic and concrete image of operator
	def _do_bin_op(self, other, fun, ast_op):
		from symbolic_expression import SymbolicExpression # dodge circular reference
		left_expr, left_concr = self.getExprConcr()
		if isinstance(other, int) or isinstance(other, long):
			right_expr = other
			right_concr = other
		elif isinstance(other, SymbolicType):
			right_expr, right_concr = other.getExprConcr()
		else:
			return NotImplemented
		aux = ast.BinOp(left=left_expr, op=ast_op(), right=right_expr)
		ret = SymbolicExpression(aux)
		ret.concrete_value = fun(left_concr, right_concr)
		# DEBUG
		#print ret
		#print ret.concrete_value
		return ret

	def getConcrValue(self):
		return self.concrete_value

	def setConcrValue(self, value):
		self.concrete_value = value

	def __getstate__(self):
		filtered_dict = {}
		filtered_dict["concrete_value"] = self.concrete_value
		return filtered_dict

	# Integer results only from now on... :(
	# also, non-standard interpretation of Python integers
	
	def __add__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x+y), ast.Add)
	def __radd__(self,other):
		return self.__add__(other)

	def __sub__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x - y), ast.Sub)
	def __rsub__(self,other):
		return self.__sub__(other)

	def __mul__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x*y), ast.Mult)
	def __rmul__(self,other):
		return self.__mul__(other)

	def __and__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x & y), ast.BitAnd)
	def __rand__(self,other):
		return self.__and__(other)

	def __or__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x | y), ast.BitOr)
	def __ror__(self,other):
		return self.__or__(other)

	def __xor__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x ^ y), ast.BitXor)
	def __rxor__(self,other):
		return self.__xor__(other)

	def __lshift__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x << y), ast.LShift)
	def __rlshift__(self,other):
		return self.__lshift__(other)

	def __rshift__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x >> y), ast.RShift)
	def __rrshift__(self,other):
		return self.__rshift__(other)

