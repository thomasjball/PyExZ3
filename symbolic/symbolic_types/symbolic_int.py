# Copyright: copyright.txt

import ast
import sys
from . symbolic_type import SymbolicType

# we use multiple inheritance to achieve concrete execution for any
# operation for which we don't have a symbolic representation. As
# we can see a SymbolicInteger is both symbolic (SymbolicType) and 
# concrete (int)

wrap = lambda conc, sym : SymbolicInteger("se",conc,sym)

class SymbolicInteger(SymbolicType,int):
	# since we are inheriting from int, we need to use new
	# to perform construction correctly
	def __new__(cls, name, v, expr=None):
		return int.__new__(cls, v)

	def __init__(self, name, v, expr=None):
		SymbolicType.__init__(self, name, expr)
		self.val = v

	# we must ensure that we are no longer inheriting from SymbolicType
	def getConcrValue(self):
		return self.val

	def __hash__(self):
		return hash(self.val)

	def __add__(self, other):
		return self._do_bin_op(other, lambda x, y: x+y, ast.Add, wrap)
	def __radd__(self,other):
		return self.__add__(other)

	def __sub__(self, other):
		return self._do_bin_op(other, lambda x, y: x - y, ast.Sub, wrap)
	def __rsub__(self,other):
		return self.__sub__(other)

	def __mul__(self, other):
		return self._do_bin_op(other, lambda x, y: x*y, ast.Mult, wrap)
	def __rmul__(self,other):
		return self.__mul__(other)

	def __mod__(self, other):
		return self._do_bin_op(other, lambda x, y: x % y, ast.Mod, wrap)
	def __rmod__(self,other):
		return self.__mod__(other)

	def __div__(self, other):
		return self._do_bin_op(other, lambda x, y: x / y, ast.Div, wrap)
	def __rdiv__(self,other):
		return self.__div__(other)

	# bit level operations

	def __and__(self, other):
		return self._do_bin_op(other, lambda x, y: x & y, ast.BitAnd, wrap)
	def __rand__(self,other):
		return self.__and__(other)

	def __or__(self, other):
		return self._do_bin_op(other, lambda x, y: x | y, ast.BitOr, wrap)
	def __ror__(self,other):
		return self.__or__(other)

	def __xor__(self, other):
		return self._do_bin_op(other, lambda x, y: x ^ y, ast.BitXor, wrap)
	def __rxor__(self,other):
		return self.__xor__(other)

	def __lshift__(self, other):
		return self._do_bin_op(other, lambda x, y: x << y, ast.LShift, wrap)
	def __rlshift__(self,other):
		return self.__lshift__(other)

	def __rshift__(self, other):
		return self._do_bin_op(other, lambda x, y: x >> y, ast.RShift, wrap)
	def __rrshift__(self,other):
		return self.__rshift__(other)

	# no symbolic implementation for
	#
	# __floordiv__
	# __divmod__
	# __pow__
	# __bit_length__

