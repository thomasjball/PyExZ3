import logging

log = logging.getLogger("se.cvc_expr.expr")


class CVCExpression(object):
    def __init__(self):
        pass

    @staticmethod
    def variable(name, solver):
        raise NotImplementedError

    @staticmethod
    def constant(v, solver):
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
