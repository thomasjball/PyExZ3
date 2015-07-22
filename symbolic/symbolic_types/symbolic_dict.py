import ast
import sys
from .symbolic_type import SymbolicObject


# SymbolicDict: the key and values will both be SymbolicType for full generality

# keys of dictionary must be immutable
# values in dictionary may be mutable


# TODO: big simplification: can only initialize with
# an empty dictionary
class SymbolicDict(SymbolicObject, dict):
    def __new__(cls, name, *args, **kwargs):
        self = dict.__new__(cls, args, kwargs)
        return self

    def __init__(self, name, kwargs):
        SymbolicObject.__init__(self, name, None)
        dict.__init__(self, kwargs)

    def getConcrValue(self):
        return self

    def __bool__(self):
        return bool(len(self))

# def wrap(conc,sym):
#		pass # TODO

#	def __getitem__(self,key):
#		val = super.__getitem__(key)
#		if isinstance(val,SymbolicType):
#			wrap = val.wrap
#		else:
#			wrap = lambda c,s : c
#		return self._do_bin_op(key, lambda d, k: val, ast.Index, wrap)

#	def __setitem__(self,key,value):
#		# update the expression (this is a triple - not binary)
#		concrete, symbolic =\
#			self._do_sexpr([self,key,value], lambda d, k, v : d.super.__setitem__(k,v), ast.Store,\
#					lambda c, s: c, s)
#		# note that we do an in place update of 
#                self.expr = symbolic

#	def __contains__(self,key):
#		for k in self.keys():
#			if k == key:
#				return True
#		return False

#	def __delitem__(self,key)
#		if dict.__contains(self,key):
#			pass
#			# self.expr = Delete(self.expr,key)
#		dict.__delitem__(self,key)
