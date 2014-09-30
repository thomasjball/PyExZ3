import ast
import utils

from symbolic.symbolic_types.symbolic_int import SymbolicInteger
from symbolic.symbolic_types.symbolic_type import SymbolicType
from z3 import *

class Z3Expression(object):
	def __init__(self):
		self.z3_vars = {}

	def toZ3(self,solver,asserts,query):
		self.z3_vars = {}
		solver.assert_exprs([self.predToZ3(p,solver) for p in asserts])
		solver.assert_exprs(Not(self.predToZ3(query,solver)))

	def predToZ3(self,pred,solver,env=None):
		sym_expr = self._astToZ3Expr(pred.symtype,solver,env)
		if env == None:
			if not is_bool(sym_expr):
				sym_expr = sym_expr != self._constant(0,solver)
			if not pred.result:
				sym_expr = Not(sym_expr)
		else:
			if not pred.result:
				sym_expr = not sym_expr
		return sym_expr

	def getIntVars(self):
		return [ v[1] for v in self.z3_vars.items() if self._isIntVar(v[1]) ]

	# ----------- private ---------------

	def _isIntVar(self, v):
		raise NotImplementedException

	def _getIntegerVariable(self,name,solver):
		if name not in self.z3_vars:
			self.z3_vars[name] = self._variable(name,solver)
		return self.z3_vars[name]

	def _variable(self,name,solver):
		raise NotImplementedException

	def _constant(self,v,solver):
		raise NotImplementedException

	def _wrapIf(self,e,solver,env):
		if env == None:
			return If(e,self._constant(1,solver),self._constant(0,solver))
		else:
			return e

	# add concrete evaluation to this, to check
	def _astToZ3Expr(self,expr,solver,env=None):
		if isinstance(expr, list):
			op = expr[0]
			args = [ self._astToZ3Expr(a,solver,env) for a in expr[1:] ]
			z3_l,z3_r = args[0],args[1]

			# arithmetical operations
			if isinstance(op, ast.Add):
				return self._add(z3_l, z3_r, solver)
			elif isinstance(op, ast.Sub):
				return self._sub(z3_l, z3_r, solver)
			elif isinstance(op, ast.Mult):
				return self._mul(z3_l, z3_r, solver)
			elif isinstance(op, ast.Div):
				return self._div(z3_l, z3_r, solver)
			elif isinstance(op, ast.Mod):
				return self._mod(z3_l, z3_r, solver)

			# bitwise
			elif isinstance(op, ast.LShift):
				return self._lsh(z3_l, z3_r, solver)
			elif isinstance(op, ast.RShift):
				return self._rsh(z3_l, z3_r, solver)
			elif isinstance(op, ast.BitXor):
				return self._xor(z3_l, z3_r, solver)
			elif isinstance(op, ast.BitOr):
				return self._or(z3_l, z3_r, solver)
			elif isinstance(op, ast.BitAnd):
				return self._and(z3_l, z3_r, solver)

			# equality gets coerced to integer
			elif isinstance(op, ast.Eq):
				return self._wrapIf(z3_l == z3_r,solver,env)
			elif isinstance(op, ast.NotEq):
				return self._wrapIf(z3_l != z3_r,solver,env)
			elif isinstance(op, ast.Lt):
				return self._wrapIf(z3_l < z3_r,solver,env)
			elif isinstance(op, ast.Gt):
				return self._wrapIf(z3_l > z3_r,solver,env)
			elif isinstance(op, ast.LtE):
				return self._wrapIf(z3_l <= z3_r,solver,env)
			elif isinstance(op, ast.GtE):
				return self._wrapIf(z3_l >= z3_r,solver,env)
			else:
				utils.crash("Unknown BinOp during conversion from ast to Z3 (expressions): %s" % op)

		elif isinstance(expr, SymbolicInteger):
			if expr.isVariable():
				if env == None:
					return self._getIntegerVariable(expr.name,solver)
				else:
					return env[expr.name]
			else:
				return self._astToZ3Expr(expr.expr,solver,env)

		elif isinstance(expr, SymbolicType):
			return self._astToZ3Expr(expr.symtype,solver,env)

		elif isinstance(expr, int):
			if env == None:
				return self._constant(expr,solver)
			else:
				return expr
		else:
			utils.crash("Unknown node during conversion from ast to Z3 (expressions): %s" % expr)

	def _add(self, l, r, solver):
		return l + r

	def _sub(self, l, r, solver):
		return l - r

	def _mul(self, l, r, solver):
		return l * r

	def _div(self, l, r, solver):
		return l / r

	def _mod(self, l, r, solver):
		return l % r

	def _lsh(self, l, r, solver):
		return l << r

	def _rsh(self, l, r, solver):
		return l >> r

	def _xor(self, l, r, solver):
		return l ^ r

	def _or(self, l, r, solver):
		return l | r

	def _and(self, l, r, solver):
		return l & r
