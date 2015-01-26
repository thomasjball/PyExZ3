from . symbolic_type import SymbolicObject
from symbolic.symbolic_types.symbolic_int import SymbolicInteger

class SymbolicStr(SymbolicObject, str):

    def __new__(cls, name, v, expr=None):
        return str.__new__(cls, v)

    def __init__(self, name, v, expr=None):
        SymbolicObject.__init__(self, name, expr)
        self.val = v

    def getConcrValue(self):
        return self.val

    def wrap(conc, sym):
        return SymbolicStr("se", conc, sym)

    def __hash__(self):
        return hash(self.val)

    def _op_worker(self, args, fun, op):
        return self._do_sexpr(args, fun, op, SymbolicStr.wrap)

    def __bool__(self):
        return SymbolicObject.__bool__(self.__len__() != 0)

    def __len__(self):
        return self._do_sexpr([self], lambda x: len(x),
                                "str.len", SymbolicInteger.wrap)

    def __contains__(self, item):
        return self._do_sexpr([self, item], lambda x, y: str.__contains__(x, y),
                                "in", SymbolicInteger.wrap)

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = key.start if key.start is not None else 0
            stop = key.stop if key.stop is not None else self.__len__()
            return self._do_sexpr([self, start, stop],
                                  lambda x, y, z: str.__getitem__(x, slice(y, z)), "slice", SymbolicStr.wrap)
        return self._do_sexpr([self, key], lambda x, y: str.__getitem__(x, y),
                              "getitem", SymbolicStr.wrap)

    def find(self, findstr):
        return self._do_sexpr([self, findstr], lambda x, y: str.find(x, findstr), 
                                "str.find", SymbolicInteger.wrap)

# Currently only a subset of string operations are supported.
ops = [("add", "+")]

def make_method(method,op,a):
    code  = "def %s(self,other):\n" % method
    code += "   return self._op_worker(%s,lambda x,y : x %s y, \"%s\")" % (a,op,op)
    locals_dict = {}
    exec(code, globals(), locals_dict)
    setattr(SymbolicStr, method, locals_dict[method])

for (name,op) in ops:
    method  = "__%s__" % name
    make_method(method,op,"[self,other]")
    rmethod  = "__r%s__" % name
    make_method(rmethod,op,"[other,self]")

