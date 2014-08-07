import ast
import sys
from . symbolic_type import SymbolicType

# SymbolicDict: the key and values will both be SymbolicType for full generality

# keys of dictionary must be immutable
# values in dictionary may be mutable

class SymbolicDict(SymbolicType,dict):
	def __new__(cls, name, v, expr=None):
		return dict.__new__(cls, v)

	def __init__(self, name, v, expr=None):
		SymbolicType.__init__(self, name, expr)
		self.log = []

	def getConcrValue(self):
		return self

	def __length__(self):
		return dict.__length__(self)

	# wrap the lvalue so that we maintain a pointer
	# to the SymbolicDict log, which will allow us
	# generate a load around the proper sequence of 
	# stores/deletes

	def __getitem__(self,key):
		return self._do_bin_op(key, lambda d, k: d[k], ast.Index)

		# create a new SymbolicType for
		# value at d[key], the expression of this 
		# SymbolicType will be Select(SymbolicDict,key)
		log.append(("SELECT",key))
		raise NotImplemented()

	def __setitem__(self,key,value):
		# the log grows
		# update the super
		log.append(("STORE",key,value))
		dict.__setitem__(self,key,value)

	def __contains__(self,key):
		for k in self.keys():
			if k == key:
				return True
		return False

	def __delitem__(self,key)
		# the log grows
		# update the super
		if dict.__contains(self,key):
			log.append(("DELETE",key))
		dict.__delitem__(self,key)
