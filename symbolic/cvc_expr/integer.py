import logging

import CVC4
from CVC4 import Rational, Integer

from .expression import CVCExpression

log = logging.getLogger("se.cvc.integer")


class CVCInteger(CVCExpression):
    _bv_size = 64

    def _isIntVar(self, v):
        return isinstance(v, IntRef)

    def _variable(self, name, solver):
        em = solver.getExprManager()
        return em.mkVar(name, em.integerType())

    def _constant(self, v, solver):
        em = solver.getExprManager()
        const_expr = em.mkConst(Rational(Integer(str(v))))
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

    def _or(self, l, r, solver):
        em = solver.getExprManager()
        #CVC4.IntToBitVector(self._bv_size)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, em.mkExpr(CVC4.BITVECTOR_OR, em.mkExpr(CVC4.INT_TO_BITVECTOR, l, self._bv_size),
                         em.mkExpr(CVC4.INT_TO_BITVECTOR, r, self._bv_size)))

    def _and(self, l, r, solver):
        em = solver.getExprManager()
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, em.mkExpr(CVC4.BITVECTOR_AND, em.mkExpr(CVC4.INT_TO_BITVECTOR, l, self._bv_size),
                         em.mkExpr(CVC4.INT_TO_BITVECTOR, r, self._bv_size)))