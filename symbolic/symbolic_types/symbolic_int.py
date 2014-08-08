# Copyright: copyright.txt

import ast
import sys
from . symbolic_type import SymbolicType

# we use multiple inheritance to achieve concrete execution for any
# operation for which we don't have a symbolic representation. As
# we can see a SymbolicInteger is both symbolic (SymbolicType) and 
# concrete (int)

class SymbolicInteger(SymbolicType,int):
	# since we are inheriting from int, we need to use new
	# to perform construction correctly
	def __new__(cls, name, v, expr=None):
		return int.__new__(cls, v)

	def __init__(self, name, v, expr=None):
		SymbolicType.__init__(self, name, expr)
		self.val = v

	def getConcrValue(self):
		return self.val

	def wrap(conc,sym):
		return SymbolicInteger("se",conc,sym)

	def __hash__(self):
		return hash(self.val)

	def __add__(self, other):
		return self._do_bin_op(other, lambda x, y: x+y, ast.Add, SymbolicInteger.wrap)
	def __radd__(self,other):
		return self.__add__(other)

	def __sub__(self, other):
		return self._do_bin_op(other, lambda x, y: x - y, ast.Sub, SymbolicInteger.wrap)
	def __rsub__(self,other):
		return self.__sub__(other)

	def __mul__(self, other):
		return self._do_bin_op(other, lambda x, y: x*y, ast.Mult, SymbolicInteger.wrap)
	def __rmul__(self,other):
		return self.__mul__(other)

	def __mod__(self, other):
		return self._do_bin_op(other, lambda x, y: x % y, ast.Mod, SymbolicInteger.wrap)
	def __rmod__(self,other):
		return self.__mod__(other)

	def __div__(self, other):
		return self._do_bin_op(other, lambda x, y: x / y, ast.Div, SymbolicInteger.wrap)
	def __rdiv__(self,other):
		return self.__div__(other)

	# bit level operations

	def __and__(self, other):
		return self._do_bin_op(other, lambda x, y: x & y, ast.BitAnd, SymbolicInteger.wrap)
	def __rand__(self,other):
		return self.__and__(other)

	def __or__(self, other):
		return self._do_bin_op(other, lambda x, y: x | y, ast.BitOr, SymbolicInteger.wrap)
	def __ror__(self,other):
		return self.__or__(other)

	def __xor__(self, other):
		return self._do_bin_op(other, lambda x, y: x ^ y, ast.BitXor, SymbolicInteger.wrap)
	def __rxor__(self,other):
		return self.__xor__(other)

	def __lshift__(self, other):
		return self._do_bin_op(other, lambda x, y: x << y, ast.LShift, SymbolicInteger.wrap)
	def __rlshift__(self,other):
		return self.__lshift__(other)

	def __rshift__(self, other):
		return self._do_bin_op(other, lambda x, y: x >> y, ast.RShift, SymbolicInteger.wrap)
	def __rrshift__(self,other):
		return self.__rshift__(other)

	# no symbolic implementation for
	#
	# __floordiv__
	# __divmod__
	# __pow__
	# __bit_length__

