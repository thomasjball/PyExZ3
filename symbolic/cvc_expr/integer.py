import logging

import CVC4
from CVC4 import Rational, Integer

from .expression import CVCExpression

log = logging.getLogger("se.cvc.integer")


class CVCInteger(CVCExpression):
    _bv_size = 8

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
        calculation = em.mkExpr(CVC4.BITVECTOR_OR, self._tobv(l, solver), self._tobv(r, solver))
        self._assert_bvsanity(l, solver)
        self._assert_bvsanity(r, solver)
        self._assert_bvbounds(calculation, solver)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, calculation)

    def _and(self, l, r, solver):
        em = solver.getExprManager()
        calculation = em.mkExpr(CVC4.BITVECTOR_AND, self._tobv(l, solver), self._tobv(r, solver))
        self._assert_bvsanity(l, solver)
        self._assert_bvsanity(r, solver)
        self._assert_bvbounds(calculation, solver)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, calculation)

    def _lsh(self, l, r, solver):
        em = solver.getExprManager()
        calculation = em.mkExpr(CVC4.BITVECTOR_SHL, self._tobv(l, solver), self._tobv(r, solver))
        self._assert_bvsanity(l, solver)
        self._assert_bvsanity(r, solver)
        self._assert_bvbounds(calculation, solver)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, calculation)

    def _rsh(self, l, r, solver):
        em = solver.getExprManager()
        calculation = em.mkExpr(CVC4.BITVECTOR_ASHR, self._tobv(l, solver), self._tobv(r, solver))
        self._assert_bvsanity(l, solver)
        self._assert_bvsanity(r, solver)
        self._assert_bvbounds(calculation, solver)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, calculation)

    def _xor(self, l, r, solver):
        em = solver.getExprManager()
        calculation = em.mkExpr(CVC4.BITVECTOR_XOR, self._tobv(l, solver), self._tobv(r, solver))
        self._assert_bvsanity(l, solver)
        self._assert_bvsanity(r, solver)
        self._assert_bvbounds(calculation, solver)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, calculation)

    def _tobv(self, expr, solver):
        em = solver.getExprManager()
        bvconversion = em.mkConst(CVC4.IntToBitVector(self._bv_size))
        return em.mkExpr(bvconversion, expr)

    def _assert_bvsanity(self, expr, solver):
        em = solver.getExprManager()
        solver.assertFormula(em.mkExpr(CVC4.EQUAL,
                                       em.mkExpr(CVC4.BITVECTOR_TO_NAT, self._tobv(expr, solver)),
                                       expr))

    def _assert_bvbounds(self, bvexpr, solver):
        em = solver.getExprManager()
        bitextract = em.mkConst(CVC4.BitVectorExtract(0, 0))
        solver.assertFormula(em.mkExpr(CVC4.EQUAL, em.mkExpr(bitextract, bvexpr),
                                       em.mkConst(CVC4.BitVector(1, 0))))