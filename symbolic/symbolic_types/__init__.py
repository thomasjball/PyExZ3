# Copyright: see copyright.txt

from .symbolic_int import SymbolicInteger as SymInt
from .symbolic_int import SymbolicObject as SymObj
from .symbolic_dict import SymbolicDict as SymD
from .symbolic_str import SymbolicStr as SymS
from .symbolic_type import SymbolicType as SymType

SymObj.wrap = lambda conc, sym: SymbolicInteger("se", conc, sym)
SymbolicInteger = SymInt
SymbolicDict = SymD
SymbolicStr = SymS
SymbolicType = SymType


def getSymbolic(v):
    exported = [(int, SymbolicInteger), (dict, SymbolicDict), (str, SymbolicStr)]
    for (t, s) in exported:
        if isinstance(v, t):
            return s
    return None
