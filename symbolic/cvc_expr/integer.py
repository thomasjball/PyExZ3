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

    CVC_TYPE = 'Int'

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

    def getvalue(self):
        """In order to mitigate the limited accuracy of the C-type values returned by the CVC getters, strings are parsed
        into Python numbers. This fix was added to pass the PyExZ3/test/bignum.py test case."""
        ce = self.solver.getValue(self.cvc_expr)
        rational = ce.getConstRational()
        numerator = int(rational.getNumerator().toString())
        denominator = int(rational.getDenominator().toString())
        if rational.isIntegral():
            return numerator // denominator
        else:
            return numerator / denominator

    def __add__(self, other):
        return CVCInteger(self.em.mkExpr(CVC4.PLUS, self.cvc_expr, other.cvc_expr), self.solver)

    def __sub__(self, other):
        return CVCInteger(self.em.mkExpr(CVC4.MINUS, self.cvc_expr, other.cvc_expr), self.solver)

    def __mul__(self, other):
        return CVCInteger(self.em.mkExpr(CVC4.MULT, self.cvc_expr, other.cvc_expr), self.solver)

    def __truediv__(self, other):
        return CVCInteger(self.em.mkExpr(CVC4.DIVISION, self.cvc_expr, other.cvc_expr), self.solver)

    def __mod__(self, other):
        return CVCInteger(self.em.mkExpr(CVC4.INTS_MODULUS, self.cvc_expr, other.cvc_expr), self.solver)

    def __or__(self, other):
        return self._bvhelper(other, CVC4.BITVECTOR_OR)

    def __and__(self, other):
        return self._bvhelper(other, CVC4.BITVECTOR_AND)

    def __xor__(self, other):
        return self._bvhelper(other, CVC4.BITVECTOR_XOR)

    def __lshift__(self, other):
        return self._bvhelper(other, CVC4.BITVECTOR_SHL)

    def __rshift__(self, other):
        return self._bvhelper(other, CVC4.BITVECTOR_ASHR)

    def tobv(self):
        bvconversion = self.em.mkConst(CVC4.IntToBitVector(self._bv_size))
        return self.em.mkExpr(bvconversion, self.cvc_expr)

    def bvsanity(self):
        return self == CVCExpression(self.em.mkExpr(CVC4.BITVECTOR_TO_NAT, self.tobv()), self.solver)

    def _bvhelper(self, other, op):
        calculation = self.em.mkExpr(op, self.tobv(), other.tobv())
        self.solver.guards.append(self.bvsanity() & other.bvsanity())
        self._assert_bvbounds(calculation)
        return CVCInteger(self.em.mkExpr(CVC4.BITVECTOR_TO_NAT, calculation), self.solver)

    def _assert_bvbounds(self, bvexpr):
        bitextract = self.em.mkConst(CVC4.BitVectorExtract(0, 0))
        self.solver.guards.append((CVCExpression(
            self.em.mkExpr(CVC4.EQUAL, self.em.mkExpr(bitextract, bvexpr),
                           self.em.mkConst(CVC4.BitVector(1, 0))),
            self.solver)))
