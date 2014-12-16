import logging

import CVC4

from .expression import CVCExpression

log = logging.getLogger("se.cvc.string")


class CVCString(CVCExpression):

    def _variable(self, name, solver):
        em = solver.getExprManager()
        return em.mkVar(name, em.stringType())

    def _constant(self, v, solver):
        em = solver.getExprManager()
        log.debug("Creating CVC4 string constant: %s" % v)
        const_expr = em.mkConst(CVC4.String(v))
        log.debug("CVC4 String expression: %s" % const_expr)
        return const_expr
