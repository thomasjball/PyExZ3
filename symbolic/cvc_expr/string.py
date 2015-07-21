import logging

import CVC4

from .expression import CVCExpression
from .integer import CVCInteger

log = logging.getLogger("se.cvc.string")


class CVCString(CVCExpression):
    CVC_TYPE = 'String'

    @classmethod
    def variable(cls, name, solver):
        em = solver.getExprManager()
        expr = em.mkVar(name, em.stringType())
        return cls(expr, solver)

    @classmethod
    def constant(cls, v, solver):
        em = solver.getExprManager()

        chararray = [CVC4.CVC4String_convertCharToUnsignedInt(c)
                     for c in bytes(v, 'UTF-8')]
        cvcstr = CVC4.CVC4String(chararray)
        assert cvcstr.size() == len(v)
        return cls(em.mkConst(cvcstr), solver)

    def getvalue(self):
        ce = self.solver.getValue(self.cvc_expr)
        chararray = [CVC4.CVC4String_convertUnsignedIntToChar(c)
                     for c in ce.getConstString().getVec()]
        v = bytes(chararray).decode()
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
            self.solver.guards.append(item.start
                                      >= CVCInteger.constant(0, self.solver))
            self.solver.guards.append(offset
                                      >= CVCInteger.constant(0, self.solver))
            # Adding these forms of guards globally
            # can limit the number of solutions generated
            # but restructuring to avoid reducing the
            # solution space is a significant undertaking.
            self.solver.guards.append(self.len() > item.start)
            self.solver.guards.append(self.len() >= item.stop)
            return CVCString(self.em.mkExpr(CVC4.STRING_SUBSTR, self.cvc_expr,
                                            item.start.cvc_expr, offset.cvc_expr),
                             self.solver)
        return CVCString(self.em.mkExpr(CVC4.STRING_CHARAT, self.cvc_expr,
                                        item.cvc_expr), self.solver)

    def find(self, findstr, beg):
        """CVC4's String IndexOf functionality is capable of specifying
        an index to begin the search. However, the current
        implementation searches from the beginning of the string."""
        return CVCInteger(
            self.em.mkExpr(CVC4.STRING_STRIDOF, self.cvc_expr,
                           findstr.cvc_expr, beg.cvc_expr),
            self.solver)

    def replace(self, old, new):
        return CVCString(self.em.mkExpr(CVC4.STRING_STRREPL, self.cvc_expr, old.cvc_expr, new.cvc_expr), self.solver)

    def startswith(self, prefix):
        return CVCExpression(self.em.mkExpr(CVC4.STRING_PREFIX,
                                            prefix.cvc_expr,
                                            self.cvc_expr), self.solver)
