# Copyright: see copyright.txt

from .symbolic_int import SymbolicInteger as SymInt
from .symbolic_dict import SymbolicDict as SymD
from .symbolic_type import SymbolicType as SymType

SymType.wrap = lambda conc, sym : SymbolicInteger("se",conc,sym)
SymbolicInteger = SymInt
SymbolicDict = SymD
SymbolicType = SymType

def getSymbolic(v):
	exported = [(int,SymbolicInteger),(dict,SymbolicDict)]
	for (t,s) in exported:
		if isinstance(v,t):
			return s
	return None



