from . symbolic_type import SymbolicObject

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

# Currently no String operations are supported.
ops =  []

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

