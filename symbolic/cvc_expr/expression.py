import utils
import logging

import CVC4

from symbolic.symbolic_types.symbolic_int import SymbolicInteger
from symbolic.symbolic_types.symbolic_type import SymbolicType

log = logging.getLogger("se.cvc_expr.expr")

class CVCExpression(object):
	def __init__(self):
		self.cvc_vars = {}

	def toCVC(self, solver, asserts, query):
		self.cvc_vars = {}
		for p in asserts:
			solver.assertFormula(self.predToCVC(p, solver))
		solver.assertFormula(solver.getExprManager().mkExpr(CVC4.NOT, self.predToCVC(query, solver)))

	def predToCVC(self,pred,solver,env=None):
		em = solver.getExprManager()				
		sym_expr = self._astToCVCExpr(pred.symtype,solver,env)
		log.debug("Converting predicate %s to CVC expression %s" % (pred, sym_expr.toString()))		
		if env == None:			
			if not CVC4.Type.isBoolean(sym_expr.getType()):				
				sym_expr = em.mkExpr(CVC4.NOT, em.mkExpr(CVC4.EQUAL, sym_expr, self._constant(0, solver)))
			if not pred.result:
				log.debug("Negating expression %s" % sym_expr.toString())
				sym_expr = em.mkExpr(CVC4.NOT, sym_expr) 				
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
		if name not in self.cvc_vars:
			self.cvc_vars[name] = self._variable(name, solver)
		return self.cvc_vars[name]

	def _variable(self,name,solver):
		raise NotImplementedException

	def _constant(self,v,solver):
		raise NotImplementedException

	def _wrapIf(self,e,solver,env):
		em = solver.getExprManager()
		if env is None:
			return em.mkExpr(CVC4.ITE, e, self._constant(1,solver), self._constant(0,solver))
		else:
			return e

	# add concrete evaluation to this, to check
	def _astToCVCExpr(self,expr,solver,env=None):
		em = solver.getExprManager()		
		logging.debug("Converting AST of type %s to CVC" % type(expr))
		
		if isinstance(expr, list):
			op = expr[0]
			args = [ self._astToCVCExpr(a,solver,env) for a in expr[1:] ]
			cvc_l,cvc_r = args[0],args[1]
			logging.debug("Joining %s with %s" % (cvc_l.toString(), cvc_r.toString()))
			# arithmetical operations
			if op == "+":
				return self._add(cvc_l, cvc_r, solver)
			elif op == "-":
				return self._sub(cvc_l, cvc_r, solver)
			elif op == "*":
				return self._mul(cvc_l, cvc_r, solver)
			elif op == "//":
				return self._div(cvc_l, cvc_r, solver)
			elif op == "%":
				return self._mod(cvc_l, cvc_r, solver)

			# bitwise
			elif op == "<<":
				return self._lsh(cvc_l, cvc_r, solver)
			elif op == ">>":
				return self._rsh(cvc_l, cvc_r, solver)
			elif op == "^":
				return self._xor(cvc_l, cvc_r, solver)
			elif op == "|":
				return self._or(cvc_l, cvc_r, solver)
			elif op == "&":
				return self._and(cvc_l, cvc_r, solver)

			# equality gets coerced to integer
			elif op == "==":
				return self._wrapIf(em.mkExpr(CVC4.EQUAL, cvc_l, cvc_r), solver, env)
			elif op == "!=":
				return self._wrapIf(cvc_l != cvc_r,solver,env)
			elif op == "<":
				return self._wrapIf(em.mkExpr(CVC4.LT, cvc_l, cvc_r), solver, env)				
			elif op == ">":
				return self._wrapIf(cvc_l > cvc_r,solver,env)
			elif op == "<=":
				return self._wrapIf(cvc_l <= cvc_r,solver,env)
			elif op == ">=":
				return self._wrapIf(cvc_l >= cvc_r,solver,env)
			else:
				utils.crash("Unknown BinOp during conversion from ast to Z3 (expressions): %s" % op)

		elif isinstance(expr, SymbolicInteger):
			if expr.isVariable():
				if env is None:
					return self._getIntegerVariable(expr.name,solver)
				else:
					return env[expr.name]
			else:
				return self._astToCVCExpr(expr.expr,solver,env)

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
