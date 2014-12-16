import utils
import logging

import CVC4

from symbolic.symbolic_types.symbolic_int import SymbolicInteger
from symbolic.symbolic_types.symbolic_type import SymbolicType

log = logging.getLogger("se.cvc_expr.expr")


class CVCExpression(object):
    def __init__(self):
        self.cvc_vars = {}

    def toCVC(self, solver, asserts, query):
        self.cvc_vars = {}
        for p in asserts:
            solver.assertFormula(self.predToCVC(p, solver))
        query = solver.getExprManager().mkExpr(CVC4.NOT, self.predToCVC(query, solver))
        log.debug("Querying solver for %s" % query.toString())
        solver.assertFormula(query)

    def predToCVC(self, pred, solver, env=None):
        em = solver.getExprManager()
        sym_expr = self._astToCVCExpr(pred.symtype, solver, env)
        log.debug("Converting predicate %s to CVC expression %s" % (pred, sym_expr.toString()))
        if env is None:
            if not CVC4.Type.isBoolean(sym_expr.getType()):
                sym_expr = em.mkExpr(CVC4.NOT, em.mkExpr(CVC4.EQUAL, sym_expr, self._constant(0, solver)))
            if not pred.result:
                sym_expr = em.mkExpr(CVC4.NOT, sym_expr)
        else:
            if not pred.result:
                sym_expr = em.mkExpr(CVC4.NOT, sym_expr)
        return sym_expr

    def _getIntegerVariable(self, name, solver):
        if name not in self.cvc_vars:
            self.cvc_vars[name] = self._variable(name, solver)
        return self.cvc_vars[name]

    def _variable(self, name, solver):
        raise NotImplementedError

    def _constant(self, v, solver):
        raise NotImplementedError

    def _wrapIf(self, expr, solver, env):
        em = solver.getExprManager()
        if env is None:
            return em.mkExpr(CVC4.ITE, expr, self._constant(1, solver), self._constant(0, solver))
        else:
            return expr

    def _astToCVCExpr(self, expr, solver, env=None):
        em = solver.getExprManager()

        if isinstance(expr, list):
            op = expr[0]
            args = [self._astToCVCExpr(a, solver, env) for a in expr[1:]]
            cvc_l, cvc_r = args[0], args[1]
            log.debug("Building %s %s %s" % (cvc_l.toString(), op, cvc_r.toString()))

            # arithmetical operations
            if op == "+":
                return self._add(cvc_l, cvc_r, solver)
            elif op == "-":
                return self._sub(cvc_l, cvc_r, solver)
            elif op == "*":
                return self._mul(cvc_l, cvc_r, solver)
            elif op == "//":
                return self._div(cvc_l, cvc_r, solver)
            elif op == "%":
                return self._mod(cvc_l, cvc_r, solver)

            # bitwise
            elif op == "<<":
                return self._lsh(cvc_l, cvc_r, solver)
            elif op == ">>":
                return self._rsh(cvc_l, cvc_r, solver)
            elif op == "^":
                return self._xor(cvc_l, cvc_r, solver)
            elif op == "|":
                return self._or(cvc_l, cvc_r, solver)
            elif op == "&":
                return self._and(cvc_l, cvc_r, solver)

            # equality gets coerced to integer
            elif op == "==":
                return self._wrapIf(em.mkExpr(CVC4.EQUAL, cvc_l, cvc_r), solver, env)
            elif op == "!=":
                return self._wrapIf(em.mkExpr(CVC4.NOT, em.mkExpr(CVC4.EQUAL, cvc_l, cvc_r)), solver, env)
            elif op == "<":
                return self._wrapIf(em.mkExpr(CVC4.LT, cvc_l, cvc_r), solver, env)
            elif op == ">":
                return self._wrapIf(em.mkExpr(CVC4.GT, cvc_l, cvc_r), solver, env)
            elif op == "<=":
                return self._wrapIf(em.mkExpr(CVC4.LEQ, cvc_l, cvc_r), solver, env)
            elif op == ">=":
                return self._wrapIf(em.mkExpr(CVC4.GEQ, cvc_l, cvc_r), solver, env)
            else:
                utils.crash("Unknown BinOp during conversion from ast to CVC (expressions): %s" % op)

        elif isinstance(expr, SymbolicInteger):
            if expr.isVariable():
                if env is None:
                    return self._getIntegerVariable(expr.name, solver)
                else:
                    return env[expr.name]
            else:
                return self._astToCVCExpr(expr.expr, solver, env)

        elif isinstance(expr, int):
            if env is None:
                return self._constant(expr, solver)
            else:
                return expr
        else:
            utils.crash("Unknown node during conversion from ast to CVC (expressions): %s" % expr)

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
