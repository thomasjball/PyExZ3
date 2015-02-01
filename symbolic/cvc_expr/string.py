import logging

import CVC4

from .expression import CVCExpression
from .integer import CVCInteger

log = logging.getLogger("se.cvc.string")


class CVCString(CVCExpression):
    @classmethod
    def variable(cls, name, solver):
        em = solver.getExprManager()
        expr = em.mkVar(name, em.stringType())
        return cls(expr, solver)

    @classmethod
    def constant(cls, v, solver):
        em = solver.getExprManager()

        # The CVC4 API requires escaping according to the SMT-LIB standard.
        cvcstr = CVC4.CVC4String(v.replace("\\", "\\\\"))
        assert cvcstr.size() == len(v)

        return cls(em.mkConst(cvcstr), solver)

    def getvalue(self):
        ce = self.solver.getValue(self.cvc_expr)
        v = ce.getConstString().toString()
        v = v.replace("\\\\", "\\")
        assert len(v) == ce.getConstString().size()
        return v

    def len(self):
        return CVCInteger(self.em.mkExpr(CVC4.STRING_LENGTH, self.cvc_expr), self.solver)

    def __add__(self, other):
        return CVCString(self.em.mkExpr(CVC4.STRING_CONCAT,
            self.cvc_expr, other.cvc_expr), self.solver)

    def __contains__(self, item):
        return CVCExpression(self.em.mkExpr(CVC4.STRING_STRCTN,
            self.cvc_expr, item.cvc_expr), self.solver)

    def __getitem__(self, item):
        if isinstance(item, slice):
            offset = item.stop - item.start
            self.solver.assertFormula((item.start < self.len()).cvc_expr)
            self.solver.assertFormula((item.start >= CVCInteger.constant(0, self.solver)).cvc_expr)
            self.solver.assertFormula((offset >= CVCInteger.constant(0, self.solver)).cvc_expr)
            return CVCString(self.em.mkExpr(CVC4.STRING_SUBSTR, self.cvc_expr, item.start.cvc_expr, offset.cvc_expr), self.solver)
        return CVCString(self.em.mkExpr(CVC4.STRING_CHARAT, self.cvc_expr, item.cvc_expr), self.solver)

    def find(self, findstr):
        """CVC4's String IndexOf functionality is capable of specifying
        an index to begin the search. However, the current
        implementation searches from the beginning of the string."""
        return CVCInteger(
            self.em.mkExpr(CVC4.STRING_STRIDOF, self.cvc_expr,
                findstr.cvc_expr, CVCInteger.constant(0, self.solver).cvc_expr),
            self.solver)

    def replace(self, old, new):
        return CVCString(self.em.mkExpr(CVC4.STRING_STRREPL, self.cvc_expr, old.cvc_expr, new.cvc_expr), self.solver)
