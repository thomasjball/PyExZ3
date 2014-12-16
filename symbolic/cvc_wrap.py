import logging

import utils

from symbolic.symbolic_types.symbolic_type import SymbolicObject
from symbolic.symbolic_types.symbolic_int import SymbolicInteger
from symbolic.symbolic_types.symbolic_str import SymbolicStr

import CVC4
from CVC4 import ExprManager, SmtEngine, SExpr

from .cvc_expr.integer import CVCInteger
from .cvc_expr.string import CVCString

log = logging.getLogger("se.cvc")


class CVCWrapper(object):
    def __init__(self):
        self.asserts = None
        self.query = None
        self.cvc_vars = {}
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
        self.cvc_vars = {}
        self._toCVC(self.asserts, self.query)
        try:
            result = self.solver.checkSat()
            log.debug("Solver returned %s" % result.toString())
            if not result.isSat():
                ret = None
            elif result.isUnknown():
                ret = None
            elif result.isSat():
                ret = self._getModel()
            else:
                raise Exception("Unexpected SMT result")
        except RuntimeError as r:
            log.debug("CVC Exception %s" % r)
            ret = None
        self.solver.pop()
        return ret

    def _getModel(self):
        """Retrieve the model generated for the path expression. Currently only rational assignments are supported.
        In order to mitigate the limited accuracy of the C-type values returned by the CVC getters, strings are parsed
        into Python numbers. This fix was added to pass the PyExZ3/test/bignum.py test case."""
        res = {}
        for name, expr in self.cvc_vars.items():
            ce = self.solver.getValue(expr)
            if ce.getType().isReal():
                rational = ce.getConstRational()
                numerator = int(rational.getNumerator().toString())
                denominator = int(rational.getDenominator().toString())
                log.debug("%s assigned to %s" % (name, ce.toString()))
                if rational.isIntegral():
                    res[name] = numerator // denominator
                else:
                    res[name] = numerator / denominator
            elif ce.getType().isString():
                res[name] = ce.getConstString().toString()
        return res
	
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

    def _toCVC(self, asserts, query):
        for p in asserts:
            self.solver.assertFormula(self._predToCVC(p))
        query = self.em.mkExpr(CVC4.NOT, self._predToCVC(query))
        log.debug("Querying solver for %s" % query.toString())
        self.solver.assertFormula(query)

    def _predToCVC(self, pred, env=None):
        sym_expr = self._astToCVCExpr(pred.symtype, env)
        log.debug("Converting predicate %s to CVC expression %s" % (pred, sym_expr.toString()))
        if env is None:
            if not CVC4.Type.isBoolean(sym_expr.getType()):
                sym_expr = self.em.mkExpr(CVC4.NOT, self.em.mkExpr(CVC4.EQUAL, sym_expr, CVCInteger.constant(0, self.solver)))
            if not pred.result:
                sym_expr = self.em.mkExpr(CVC4.NOT, sym_expr)
        else:
            if not pred.result:
                sym_expr = self.em.mkExpr(CVC4.NOT, sym_expr)
        return sym_expr

    def _getVariable(self, expr):
        name = expr.name
        if name not in self.cvc_vars:
            variable = None
            if isinstance(expr, SymbolicInteger):
                variable = CVCInteger.variable(name, self.solver)
            elif isinstance(expr, SymbolicStr):
                variable = CVCString.variable(name, self.solver)
            self.cvc_vars[name] = variable
        return self.cvc_vars[name]

    def _wrapIf(self, expr, solver, env):
        if env is None:
            return self.em.mkExpr(CVC4.ITE, expr, CVCInteger.constant(1, solver), CVCInteger.constant(0, solver))
        else:
            return expr

    def _astToCVCExpr(self, expr, env=None):
        log.debug("Converting %s (type: %s) to CVC expression" % (expr, type(expr)))
        if isinstance(expr, list):
            op = expr[0]
            args = [self._astToCVCExpr(a, env) for a in expr[1:]]
            cvc_l, cvc_r = args[0], args[1]
            log.debug("Building %s %s %s" % (cvc_l.toString(), op, cvc_r.toString()))

            optype = None

            if cvc_l.getType().isInteger() or cvc_l.getType().isReal():
                optype = CVCInteger()
            elif cvc_l.getType().isString():
                optype = CVCString()
            else:
                utils.crash("Unknown operand type during conversion from ast to CVC (expressions): %s" % cvc_l.getType().toString())

            # arithmetical operations
            if op == "+":
                return optype.add(cvc_l, cvc_r, self.solver)
            elif op == "-":
                return optype.sub(cvc_l, cvc_r, self.solver)
            elif op == "*":
                return optype.mul(cvc_l, cvc_r, self.solver)
            elif op == "//":
                return optype.div(cvc_l, cvc_r, self.solver)
            elif op == "%":
                return optype.mod(cvc_l, cvc_r, self.solver)

            # bitwise
            elif op == "<<":
                return optype.lsh(cvc_l, cvc_r, self.solver)
            elif op == ">>":
                return optype.rsh(cvc_l, cvc_r, self.solver)
            elif op == "^":
                return optype.xor(cvc_l, cvc_r, self.solver)
            elif op == "|":
                return optype.orop(cvc_l, cvc_r, self.solver)
            elif op == "&":
                return optype.andop(cvc_l, cvc_r, self.solver)

            # equality gets coerced to integer
            elif op == "==":
                return self._wrapIf(self.em.mkExpr(CVC4.EQUAL, cvc_l, cvc_r), self.solver, env)
            elif op == "!=":
                return self._wrapIf(self.em.mkExpr(CVC4.NOT, self.em.mkExpr(CVC4.EQUAL, cvc_l, cvc_r)), self.solver, env)
            elif op == "<":
                return self._wrapIf(self.em.mkExpr(CVC4.LT, cvc_l, cvc_r), self.solver, env)
            elif op == ">":
                return self._wrapIf(self.em.mkExpr(CVC4.GT, cvc_l, cvc_r), self.solver, env)
            elif op == "<=":
                return self._wrapIf(self.em.mkExpr(CVC4.LEQ, cvc_l, cvc_r), self.solver, env)
            elif op == ">=":
                return self._wrapIf(self.em.mkExpr(CVC4.GEQ, cvc_l, cvc_r), self.solver, env)
            else:
                utils.crash("Unknown BinOp during conversion from ast to CVC (expressions): %s" % op)

        elif isinstance(expr, SymbolicObject):
            if expr.isVariable():
                if env is None:
                    return self._getVariable(expr)
                else:
                    return env[expr.name]
            else:
                return self._astToCVCExpr(expr.expr, env)

        elif isinstance(expr, int) | isinstance(expr, str):
            if env is None:
                if isinstance(expr, int):
                    return CVCInteger.constant(expr, self.solver)
                elif isinstance(expr, str):
                    return CVCString.constant(expr, self.solver)
            else:
                return expr

        else:
            utils.crash("Unknown node during conversion from ast to CVC (expressions): %s" % expr)