import logging

import CVC4
from CVC4 import Rational, Integer

from .expression import CVCExpression

log = logging.getLogger("se.cvc.integer")


class CVCInteger(CVCExpression):
    _bv_size = 8

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
        bvconversion = em.mkConst(CVC4.IntToBitVector(self._bv_size))
        lbitvector = em.mkExpr(bvconversion, l)
        rbitvector = em.mkExpr(bvconversion, r)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, em.mkExpr(CVC4.BITVECTOR_OR, lbitvector, rbitvector))

    def _and(self, l, r, solver):
        em = solver.getExprManager()
        bvconversion = em.mkConst(CVC4.IntToBitVector(self._bv_size))
        lbitvector = em.mkExpr(bvconversion, l)
        rbitvector = em.mkExpr(bvconversion, r)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, em.mkExpr(CVC4.BITVECTOR_AND, lbitvector, rbitvector))

    def _lsh(self, l, r, solver):
        em = solver.getExprManager()
        bvconversion = em.mkConst(CVC4.IntToBitVector(self._bv_size))
        lbitvector = em.mkExpr(bvconversion, l)
        rbitvector = em.mkExpr(bvconversion, r)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, em.mkExpr(CVC4.BITVECTOR_SHL, lbitvector, rbitvector))

    def _rsh(self, l, r, solver):
        em = solver.getExprManager()
        bvconversion = em.mkConst(CVC4.IntToBitVector(self._bv_size))
        lbitvector = em.mkExpr(bvconversion, l)
        rbitvector = em.mkExpr(bvconversion, r)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, em.mkExpr(CVC4.BITVECTOR_ASHR, lbitvector, rbitvector))

    def _xor(self, l, r, solver):
        em = solver.getExprManager()
        bvconversion = em.mkConst(CVC4.IntToBitVector(self._bv_size))
        lbitvector = em.mkExpr(bvconversion, l)
        rbitvector = em.mkExpr(bvconversion, r)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, em.mkExpr(CVC4.BITVECTOR_XOR, lbitvector, rbitvector))