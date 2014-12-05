import logging

from CVC4 import Rational

from .expression import CVCExpression

log = logging.getLogger("se.cvc.integer")

class CVCInteger(CVCExpression):
	def _isIntVar(self,v):
		return isinstance(v,IntRef)

	def _variable(self,name,solver):
		em = solver.getExprManager()
		return em.mkVar(name, em.integerType()) 

	def _constant(self,v,solver):
		em = solver.getExprManager()
		const_expr = em.mkConst(Rational(v))
		logging.debug("Created constant expression %s from %s" % (const_expr.toString(), v))
		return const_expr

	def _mod(self, l, r, solver):
		mod_fun = Function('int_mod', IntSort(), IntSort(), IntSort())
		return mod_fun(l, r)

	def _lsh(self, l, r, solver):
		lsh_fun = Function('int_lsh', IntSort(), IntSort(), IntSort())
		return lsh_fun(l, r)

	def _rsh(self, l, r, solver):
		rsh_fun = Function('int_rsh', IntSort(), IntSort(), IntSort())
		return rsh_fun(l, r)

	def _xor(self, l, r, solver):
		xor_fun = Function('int_xor', IntSort(), IntSort(), IntSort())
		return xor_fun(l, r)

	def _or(self, l, r, solver):
		or_fun = Function('int_or', IntSort(), IntSort(), IntSort())
		return or_fun(l, r)

	def _and(self, l, r, solver):
		and_fun = Function('int_and', IntSort(), IntSort(), IntSort())
		return and_fun(l, r)
