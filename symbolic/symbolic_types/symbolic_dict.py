
import ast
import sys
from . symbolic_type import SymbolicType

class SymbolicDict(SymbolicType,dict):
	def __new__(cls, name, v, expr=None):
		return dict.__new__(cls, v)

	def __init__(self, name, v, expr=None):
		SymbolicType.__init__(self, name, expr)
		self.val = v

	def wrap(self,conc,sym):
		return SymbolicInteger("se",conc,sym)
	
	def getConcrValue(self):
		return self

	#def __length__(self):
	#	pass

	# wrap the lvalue so that we maintain a pointer
	# to the SymbolicDict log, which will allow us
	# generate a load around the proper sequence of 
	# stores/deleles

	def __getitem__(self,key):
		pass

	def __setitem__(self,key,value):
		# the expression grows
		# update the super
		pass

	def __contains__(self,key):
		pass

	def __delitem__(self,key)
		# the expression grows
		# update the super
		pass
