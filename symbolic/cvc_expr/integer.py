import logging

import CVC4
from CVC4 import Rational, Integer

from .expression import CVCExpression

log = logging.getLogger("se.cvc.integer")


class CVCInteger(CVCExpression):
    def _isIntVar(self, v):
        return isinstance(v, IntRef)

    def _variable(self, name, solver):
        em = solver.getExprManager()
        return em.mkVar(name, em.integerType())

    def _constant(self, v, solver):
        em = solver.getExprManager()
        const_expr = em.mkConst(Rational(Integer(v)))
        return const_expr

    def _add(self, l, r, solver):
        em = solver.getExprManager()
        return em.mkExpr(CVC4.PLUS, l, r)

    def _sub(self, l, r, solver):
        em = solver.getExprManager()
        return em.mkExpr(CVC4.MINUS, l, r)

    def _mul(self, l, r, solver):
        em = solver.getExprManager()
        return em.mkExpr(CVC4.MULT, l, r)

    def _div(self, l, r, solver):
        em = solver.getExprManager()
        return em.mkExpr(CVC4.DIVISION, l, r)

    def _mod(self, l, r, solver):
        em = solver.getExprManager()
        return em.mkExpr(CVC4.INTS_MODULUS, l, r)