import ast
import sys
from . symbolic_type import SymbolicType

# SymbolicDict: key, values - does it make sense for them to be non-symbolic?
# (some) keys should be symbolic - otherwise, we don't have aliasing issues
# values need not be symbolic

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
		# what is it? a SymbolicType (yes, of an lvalue)
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
