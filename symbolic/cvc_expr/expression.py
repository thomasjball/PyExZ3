import logging

import CVC4


log = logging.getLogger("se.cvc_expr.expr")


class CVCExpression(object):
    def __init__(self, cvc_expr, solver):
        self.cvc_expr = cvc_expr
        self.solver = solver
        self.em = self.solver.getExprManager()

    @classmethod
    def variable(cls, name, solver):
        raise NotImplementedError

    @classmethod
    def constant(cls, v, solver):
        raise NotImplementedError

    def getvalue(self):
        raise NotImplementedError

    def ite(self, th, el):
        assert th.cvc_expr.getType().toString() == el.cvc_expr.getType().toString()
        return th.__class__(self.em.mkExpr(CVC4.ITE, self.cvc_expr,
        th.cvc_expr, el.cvc_expr), self.solver)

    def __and__(self, other):
        return CVCExpression(self.em.mkExpr(CVC4.AND, self.cvc_expr, other.cvc_expr), self.solver)

    def __xor__(self, other):
        return CVCExpression(self.em.mkExpr(CVC4.XOR, self.cvc_expr, other.cvc_expr), self.solver)

    def __or__(self, other):
        return CVCExpression(self.em.mkExpr(CVC4.OR, self.cvc_expr, other.cvc_expr), self.solver)

    def not_op(self):
        return CVCExpression(self.em.mkExpr(CVC4.NOT, self.cvc_expr), self.solver)

    def __ne__(self, other):
        return CVCExpression(self.em.mkExpr(CVC4.NOT, self.em.mkExpr(CVC4.EQUAL, self.cvc_expr, other.cvc_expr)), self.solver)

    def __eq__(self, other):
        return CVCExpression(self.em.mkExpr(CVC4.EQUAL, self.cvc_expr, other.cvc_expr), self.solver)

    def __lt__(self, other):
        return CVCExpression(self.em.mkExpr(CVC4.LT, self.cvc_expr, other.cvc_expr), self.solver)

    def __gt__(self, other):
        return CVCExpression(self.em.mkExpr(CVC4.GT, self.cvc_expr, other.cvc_expr), self.solver)

    def __ge__(self, other):
        return CVCExpression(self.em.mkExpr(CVC4.GEQ, self.cvc_expr, other.cvc_expr), self.solver)

    def __le__(self, other):
        return CVCExpression(self.em.mkExpr(CVC4.LEQ, self.cvc_expr, other.cvc_expr), self.solver)

    def __str__(self):
        return self.cvc_expr.toString()