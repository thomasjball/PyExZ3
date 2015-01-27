import logging

import utils

import CVC4
from CVC4 import ExprManager, SmtEngine, SExpr

from symbolic.cvc_expr.exprbuilder import ExprBuilder

log = logging.getLogger("se.cvc")


class CVCWrapper(object):
    def __init__(self):
        self.asserts = None
        self.query = None
        self.em = None
        self.solver = None

    def findCounterexample(self, asserts, query):
        """Tries to find a counterexample to the query while
           asserts remains valid."""
        self.em = ExprManager()
        self.solver = SmtEngine(self.em)
        self.solver.setOption("produce-models", SExpr("true"))
        self.solver.setOption("strings-exp", SExpr("true")) # Enable experimental string support
        self.solver.setOption("rewrite-divk", SExpr("true")) # Enable modular arithmetic with constant modulus
        self.solver.setOption("tlimit-per", SExpr("5000")) # Per Query timeout of 5 seconds
        self.solver.setLogic("ALL_SUPPORTED")
        self.query = query
        self.asserts = self._coneOfInfluence(asserts, query)
        result = self._findModel()
        log.debug("Query -- %s" % self.query)
        log.debug("Asserts -- %s" % asserts)
        log.debug("Cone -- %s" % self.asserts)
        log.debug("Result -- %s" % result)
        return result

    def _findModel(self):
        self.solver.push()
        exprbuilder = ExprBuilder(self.asserts, self.query, self.solver)
        try:
            result = self.solver.checkSat()
            log.debug("Solver returned %s" % result.toString())
            if not result.isSat():
                ret = None
            elif result.isUnknown():
                ret = None
            elif result.isSat():
                ret = self._getModel(exprbuilder.cvc_vars)
            else:
                raise Exception("Unexpected SMT result")
        except RuntimeError as r:
            log.debug("CVC exception %s" % r)
            ret = None
        self.solver.pop()
        return ret

    @staticmethod
    def _getModel(variables):
        """Retrieve the model generated for the path expression."""
        return {name: cvc_var.getvalue() for (name, cvc_var) in variables.items()}
	
    @staticmethod
    def _coneOfInfluence(asserts, query):
        cone = []
        cone_vars = set(query.getVars())
        ws = [a for a in asserts if len(set(a.getVars()) & cone_vars) > 0]
        remaining = [a for a in asserts if a not in ws]
        while len(ws) > 0:
            a = ws.pop()
            a_vars = set(a.getVars())
            cone_vars = cone_vars.union(a_vars)
            cone.append(a)
            new_ws = [a for a in remaining if len(set(a.getVars()) & cone_vars) > 0]
            remaining = [a for a in remaining if a not in new_ws]
            ws = ws + new_ws
        return cone
