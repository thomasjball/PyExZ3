import logging

import CVC4
from CVC4 import Rational, Integer

from .expression import CVCExpression

log = logging.getLogger("se.cvc.integer")


class CVCInteger(CVCExpression):
    """Python numbers are represented as integers in the CVC path expression. For bitwise operations, integers are
    transformed into bit vectors of size _bv_size and then converted back to a natural number using CVC's
    BITVECTOR_TO_NAT operator. In order to maintain sound reasoning of the behavior of generated inputs, all inputs to
    bit vector operations are asserted positive through _assert_bvsanity as well as the outputs through
    _assert_bvbounds. These assumptions restrict the symbolic execution from finding valid solutions to path formulas
    in order to avoid generating path expressions with solutions that do not match program behavior. For example, x = -1
    is a valid solution to x != CVC4.BITVECTOR_TO_NAT(CVC4.INT_TO_BITVECTOR(x)) since the output of the right-hand side
    of the equation will be positive (natural numbers are >= 0).

    Possible improvements:

    1) _bv_size is currently fixed at a low number. The Z3 integration starts with small bit vectors and gradually
    increases the size until a solution is found. Match that functionality in CVCInteger.

    2) Create an alternative implementation of CVCInteger that uses bit vectors for all operations. In the presence of
    bitwise operations, the conversion between bit vectors and integers is expensive.

    3) Encode in the formula a BITVECTOR_TO_INT conversion that performs two's complement arithmetic."""

    _bv_size = 8

    @classmethod
    def variable(cls, name, solver):
        em = solver.getExprManager()
        expr = em.mkVar(name, em.integerType())
        return cls(expr, solver)

    @classmethod
    def constant(cls, v, solver):
        em = solver.getExprManager()
        return cls(em.mkConst(Rational(Integer(str(v)))), solver)

    def add(self, l, r, solver):
        em = solver.getExprManager()
        return em.mkExpr(CVC4.PLUS, l, r)

    def __add__(self, other):
        return CVCInteger(self.em.mkExpr(CVC4.PLUS, self.cvc_expr, self.cvc_expr), self.solver)

    def sub(self, l, r, solver):
        em = solver.getExprManager()
        return em.mkExpr(CVC4.MINUS, l, r)

    def mul(self, l, r, solver):
        em = solver.getExprManager()
        return em.mkExpr(CVC4.MULT, l, r)

    def div(self, l, r, solver):
        em = solver.getExprManager()
        return em.mkExpr(CVC4.DIVISION, l, r)

    def mod(self, l, r, solver):
        em = solver.getExprManager()
        return em.mkExpr(CVC4.INTS_MODULUS, l, r)

    def orop(self, l, r, solver):
        em = solver.getExprManager()
        calculation = em.mkExpr(CVC4.BITVECTOR_OR, self._tobv(l, solver), self._tobv(r, solver))
        self._assert_bvsanity(l, solver)
        self._assert_bvsanity(r, solver)
        self._assert_bvbounds(calculation, solver)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, calculation)

    def andop(self, l, r, solver):
        em = solver.getExprManager()
        calculation = em.mkExpr(CVC4.BITVECTOR_AND, self._tobv(l, solver), self._tobv(r, solver))
        self._assert_bvsanity(l, solver)
        self._assert_bvsanity(r, solver)
        self._assert_bvbounds(calculation, solver)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, calculation)

    def lsh(self, l, r, solver):
        em = solver.getExprManager()
        calculation = em.mkExpr(CVC4.BITVECTOR_SHL, self._tobv(l, solver), self._tobv(r, solver))
        self._assert_bvsanity(l, solver)
        self._assert_bvsanity(r, solver)
        self._assert_bvbounds(calculation, solver)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, calculation)

    def rsh(self, l, r, solver):
        em = solver.getExprManager()
        calculation = em.mkExpr(CVC4.BITVECTOR_ASHR, self._tobv(l, solver), self._tobv(r, solver))
        self._assert_bvsanity(l, solver)
        self._assert_bvsanity(r, solver)
        self._assert_bvbounds(calculation, solver)
        return em.mkExpr(CVC4.BITVECTOR_TO_NAT, calculation)

    def xor(self, l, r, solver):
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

    @staticmethod
    def _assert_bvbounds(bvexpr, solver):
        em = solver.getExprManager()
        bitextract = em.mkConst(CVC4.BitVectorExtract(0, 0))
        solver.assertFormula(em.mkExpr(CVC4.EQUAL, em.mkExpr(bitextract, bvexpr),
                                       em.mkConst(CVC4.BitVector(1, 0))))
