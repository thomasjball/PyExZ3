import logging

import CVC4


log = logging.getLogger("se.cvc_expr.expr")


class CVCExpression(object):
    def __init__(self, cvc_expr, solver):
        self.cvc_expr = cvc_expr
        self.solver = solver
        self.em = self.solver.getExprManager()

    def __eq__(self, y):
        return CVCExpression(self.em.mkExpr(CVC4.EQUAL, self.cvc_expr, y.cvc_expr), self.solver)

    def __str__(self):
        return self.cvc_expr.toString()

    def ite(self, th, el):
        return CVCExpression(self.em.mkExpr(CVC4.ITE, self.cvc_expr, 
        th.cvc_expr, el.cvc_expr), self.solver)

    @classmethod
    def variable(cls, name, solver):
        raise NotImplementedError

    @classmethod
    def constant(cls, v, solver):
        raise NotImplementedError

    def _add(self, l, r, solver):
        return l + r

    def _sub(self, l, r, solver):
        return l - r

    def _mul(self, l, r, solver):
        return l * r

    def _div(self, l, r, solver):
        return l / r

    def _mod(self, l, r, solver):
        return l % r

    def _lsh(self, l, r, solver):
        return l << r

    def _rsh(self, l, r, solver):
        return l >> r

    def _xor(self, l, r, solver):
        return l ^ r

    def _or(self, l, r, solver):
        return l | r

    def _and(self, l, r, solver):
        return l & r

    def not_op(self):
        return CVCExpression(self.em.mkExpr(CVC4.NOT, self.cvc_expr), self.solver)
