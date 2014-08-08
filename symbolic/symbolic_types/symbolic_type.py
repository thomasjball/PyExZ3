# Copyright: see copyright.txt

import utils
import ast

# the ABSTRACT base class for representing any expression that depends on a symbolic input
# it also tracks the corresponding concrete value for the expression (aka concolic execution)

class SymbolicType(object):
	SI = None    # this is set up by ConcolicEngine to link __bool__ to PathConstraint

	def __init__(self, name, expr=None):
		self.name = name
		self.expr = expr

	def isVariable(self):
		return self.expr == None

	def unwrap(self):
		if self.isVariable():
			return (self.getConcrValue(),self)
		else:
			return (self.getConcrValue(),self.expr)

	def getConcrValue():
		raise NotImplemented()

	def wrap(conc,sym):
		raise NotImplemented()

	# this is a critical interception point: the __bool__
	# method is called whenever a predicate is evaluated in
	# Python execution (if, while, and, or). This allows us
	# to capture the path condition

	def __bool__(self):
		ret = bool(self.getConcrValue())
		if SymbolicType.SI != None:
			SymbolicType.SI.whichBranch(ret,self)
		return ret

	def __eq__(self, other):
		if isinstance(other, type(None)):
			return False
		else:
			return self._do_bin_op(other, lambda x, y: x == y, ast.Eq, SymbolicType.wrap)

	def __ne__(self, other):
		if isinstance(other, type(None)):
			return True
		else:
			return self._do_bin_op(other, lambda x, y: x != y, ast.NotEq, SymbolicType.wrap)

	def __lt__(self, other):
		return self._do_bin_op(other, lambda x, y: x < y, ast.Lt, SymbolicType.wrap)

	def __le__(self, other):
		return self._do_bin_op(other, lambda x, y: x <= y, ast.LtE, SymbolicType.wrap)

	def __gt__(self, other):
		return self._do_bin_op(other, lambda x, y: x > y, ast.Gt, SymbolicType.wrap)

	def __ge__(self, other):
		return self._do_bin_op(other, lambda x, y: x >= y, ast.GtE, SymbolicType.wrap)

	# compute both the symbolic and concrete image of operator
	# TODO: we should generalize this to s-expressions in order to 
	# to accommodate unary and function calls

	def _do_bin_op(self, other, fun, op, wrap):
		left_concr, left_expr = self.unwrap()
		if isinstance(other, SymbolicType):
			right_concr, right_expr = other.unwrap()
		else:
			right_concr, right_expr = other, other
		result_concr = fun(left_concr, right_concr)
		result_expr  = ast.BinOp(left=left_expr,op=op(),right=right_expr)
		return wrap(result_concr,result_expr)

	# BELOW HERE is only for our use

	def symbolicEq(self, other):
		if not isinstance(other,SymbolicType):
			return False;
		if self.isVariable() or other.isVariable():
			return self.name == other.name
		return self._do_symbolicEq_expr(self.expr,other.expr)

	def _do_symbolicEq_expr(self, expr1, expr2):
		if type(expr1) != type(expr2):
			return False
		if isinstance(expr1, ast.BinOp):
			res = type(expr1.op) == type(expr2.op) and\
				self._do_symbolicEq_expr(expr1.left, expr2.left) and\
		               	self._do_symbolicEq_expr(expr1.right, expr2.right)
			return res
		elif isinstance(expr1, SymbolicType):
			return expr1.name == expr2.name
		else:
			return expr1 == expr2

	def toString(self):
		if self.isVariable():
			return self.name + "#" + str(self.getConcrValue())
		else:
			return self._toString(self.expr)

	def _toString(self,expr):
		if isinstance(expr,ast.BinOp):
			return "(" + self._toString(expr.left) + " " + op2str(expr.op) + " " + self._toString(expr.right) + ")"
		elif isinstance(expr,SymbolicType):
			return expr.toString()
		else:
			return str(expr)

def op2str(o):
	if isinstance(o,ast.Add):
		return "+"
	if isinstance(o,ast.Sub):
		return "-"
	if isinstance(o,ast.Mult):
		return "*"
	if isinstance(o,ast.Div):
		return "/"
	if isinstance(o,ast.Mod):
		return "%"
	if isinstance(o,ast.Pow):
		return "**"
	if isinstance(o,ast.LShift):
		return "<<"
	if isinstance(o,ast.RShift):
		return ">>"
	if isinstance(o,ast.BitOr):
		return "|"
	if isinstance(o,ast.BitXor):
		return "^"
	if isinstance(o,ast.BitAnd):
		return "&"
	if isinstance(o,ast.FloorDiv):
		return "//"
	if isinstance(o,ast.Eq):
		return "=="
	if isinstance(o,ast.NotEq):
		return "!="
	if isinstance(o,ast.Lt):
		return "<"
	if isinstance(o,ast.Gt):
		return ">"
	if isinstance(o,ast.LtE):
		return "<="
	if isinstance(o,ast.GtE):
		return ">="
	if isinstance(o,ast.Is):
		return "is"
	if isinstance(o,ast.IsNot):
		return "is not"
	if isinstance(o,ast.In):
		return "in"
	if isinstance(o,ast.NotIn):
		return "not in"
	raise KeyError()

