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

    def find(self, findstr):
        return self._do_sexpr([self, findstr], lambda x, y: str.find(x, findstr), 
                                "str.find", SymbolicInteger.wrap)

    def count(self, sub):
        """String count is not a native function of the SMT solver. Instead, we implement count as a recursive series of
        find operations."""
        if sub == "":
            return 0
        elif sub not in self:
            return 0
        else:
            find_idx = self.find(sub)
            reststr = self[find_idx + len(sub):]
            return reststr.count(sub) + 1

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

