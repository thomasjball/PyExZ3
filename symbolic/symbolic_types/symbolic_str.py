from .symbolic_type import SymbolicObject
from symbolic.symbolic_types.symbolic_int import SymbolicInteger
from string import whitespace


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
        """Negative indexes, out of bound slices, and slice skips are not currently supported."""
        if isinstance(key, slice):
            start = key.start if key.start is not None else 0
            stop = key.stop if key.stop is not None else self.__len__()
            return self._do_sexpr([self, start, stop],
                                  lambda x, y, z: str.__getitem__(x, slice(y, z)), "slice", SymbolicStr.wrap)
        return self._do_sexpr([self, key], lambda x, y: str.__getitem__(x, y),
                              "getitem", SymbolicStr.wrap)

    def find(self, findstr, beg=0):
        return self._do_sexpr([self, findstr, beg],
                              lambda x, y, z: str.find(x, y, z),
                              "str.find", SymbolicInteger.wrap)

    def startswith(self, prefix):
        return self._do_sexpr([self, prefix],
                              lambda x, y: str.startswith(x, y),
                              "str.startswith", SymbolicInteger.wrap)

    def split(self, sep=None, maxsplit=None):
        if sep is None:
            sep = " "
        if len(self) == 0:
            return []
        elif maxsplit == 0 or sep not in self:
            return [self]
        else:
            sep_idx = self.find(sep)
            maxsplit = None if maxsplit is None else maxsplit - 1
            return [self[0:sep_idx]] + \
                   self[sep_idx + 1:].split(sep, maxsplit)

    def count(self, sub):
        """String count is not a native function of the SMT solver. Instead, we implement count as a recursive series of
        find operations. Note that not all of the functionality of count is supported at this time, such as the start
        index."""
        if sub not in self:
            ret = 0
        elif sub == "":
            ret = self.__len__() + 1
        else:
            find_idx = self.find(sub)
            reststr = self[find_idx + sub.__len__():]
            ret = reststr.count(sub) + 1
        assert int(ret) == str.count(str(self), str(sub))
        return ret

    def _replace(self, old, new):
        return self._do_sexpr([self, old, new], lambda x, y, z: str.replace(x, y, z),
                              "str.replace", SymbolicStr.wrap)

    def replace(self, old, new, maxreplace=-1):
        """CVC only replaces the first occurrence of old with new
        (maxreplace=1). For this reason, SymbolicStr's replace is implemented
        as a recurrence of single replaces."""
        if maxreplace == 0 or old not in self:
            ret = self
        else:
            pivot_point = self.find(old) + old.__len__()
            first_half = self[:pivot_point]
            first_half = first_half._replace(old, new)
            second_half = self[pivot_point:]
            ret = first_half + second_half.replace(old, new, maxreplace - 1)
        assert str(ret) == str.replace(str(self), str(old), str(new), int(maxreplace))
        return ret

    def strip(self, chars=None):
        if chars is None:
            chars = whitespace
        if self.__len__() == 0:
            return self
        for char in chars:
            if self[0] == char:
                return self[1:].strip(chars)
        for char in chars:
            if self[self.__len__() - 1] == char:
                return self[:self.__len__() - 1].strip(chars)
        return self


# Currently only a subset of string operations are supported.
ops = [("add", "+")]


def make_method(method, op, a):
    code = "def %s(self,other):\n" % method
    code += "   return self._op_worker(%s,lambda x,y : x %s y, \"%s\")" % (a, op, op)
    locals_dict = {}
    exec(code, globals(), locals_dict)
    setattr(SymbolicStr, method, locals_dict[method])


for (name, op) in ops:
    method = "__%s__" % name
    make_method(method, op, "[self,other]")
    rmethod = "__r%s__" % name
    make_method(rmethod, op, "[other,self]")
