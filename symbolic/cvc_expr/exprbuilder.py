import logging

import CVC4
from symbolic.cvc_expr.expression import CVCExpression
from symbolic.cvc_expr.integer import CVCInteger
from symbolic.cvc_expr.string import CVCString
from symbolic.symbolic_types import SymbolicInteger, SymbolicStr
from symbolic.symbolic_types.symbolic_type import SymbolicObject
import utils

log = logging.getLogger("se.cvc_expr.exprbuilder")

class ExprBuilder(object):
    def __init__(self, solver):
        self.solver = solver
        self.em = self.solver.getExprManager()
        self.cvc_vars = {}

    def toCVC(self, asserts, query):
        for p in asserts:
            self.solver.assertFormula(self._predToCVC(p).cvc_expr)
        cvc_query = self._predToCVC(query).not_op()
        log.debug("Querying solver for %s" % cvc_query)
        self.solver.assertFormula(cvc_query.cvc_expr)
        self.cvc_vars = {name: expr.cvc_expr for (name, expr) in self.cvc_vars.items()}

    
    def _predToCVC(self, pred, env=None):
        sym_expr = CVCExpression(self._astToCVCExpr(pred.symtype, env), self.solver)
        log.debug("Converting predicate %s to CVC expression %s" % (pred, sym_expr))
        if env is None:
            if not sym_expr.cvc_expr.getType().isBoolean():
                sym_expr = (sym_expr == CVCInteger.constant(0, self.solver)).not_op()
            if not pred.result:
                sym_expr = sym_expr.not_op()
        else:
            if not pred.result:
                sym_expr = sym_expr.not_op()
        return sym_expr
    
    def _getVariable(self, symbolic_var):
        name = symbolic_var.name
        if name in self.cvc_vars:
            return self.cvc_vars[name]
        variable = None
        if isinstance(symbolic_var, SymbolicInteger):
            variable = CVCInteger.variable(name, self.solver)
        elif isinstance(symbolic_var, SymbolicStr):
            variable = CVCString.variable(name, self.solver)
        self.cvc_vars[name] = variable
        return variable
    
    def _wrapIf(self, expr, env):
        if env is None:
            return self.em.mkExpr(CVC4.ITE, expr, CVCInteger.constant(1, self.solver).cvc_expr, CVCInteger.constant(0, self.solver).cvc_expr)
        else:
            return expr
    
    
    #def _wrapIf(expr, solver, env):
    #    if env is None:
    #        return CVCExpression(expr, solver).ite(CVCInteger.constant(1, solver), CVCInteger.constant(0, solver)).cvc_expr
    #    else:
    #        return expr
    
    def _astToCVCExpr(self, expr, env=None):
    
        log.debug("Converting %s (type: %s) to CVC expression" % (expr, type(expr)))
        if isinstance(expr, list):
            op = expr[0]
            args = [self._astToCVCExpr(a, env) for a in expr[1:]]
            cvc_l, cvc_r = args[0], args[1]
            log.debug("Building %s %s %s" % (cvc_l.toString(), op, cvc_r.toString()))
    
            optype = None
    
            if cvc_l.getType().isInteger() or cvc_l.getType().isReal():
                optype = CVCInteger(None, self.solver)
            elif cvc_l.getType().isString():
                optype = CVCString(None, self.solver)
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
                return self._wrapIf(self.em.mkExpr(CVC4.EQUAL, cvc_l, cvc_r), env)
            elif op == "!=":
                return self._wrapIf(self.em.mkExpr(CVC4.NOT, self.em.mkExpr(CVC4.EQUAL, cvc_l, cvc_r)), env)
            elif op == "<":
                return self._wrapIf(self.em.mkExpr(CVC4.LT, cvc_l, cvc_r), env)
            elif op == ">":
                return self._wrapIf(self.em.mkExpr(CVC4.GT, cvc_l, cvc_r), env)
            elif op == "<=":
                return self._wrapIf(self.em.mkExpr(CVC4.LEQ, cvc_l, cvc_r), env)
            elif op == ">=":
                return self._wrapIf(self.em.mkExpr(CVC4.GEQ, cvc_l, cvc_r), env)
            else:
                utils.crash("Unknown BinOp during conversion from ast to CVC (expressions): %s" % op)
    
        elif isinstance(expr, SymbolicObject):
            if expr.isVariable():
                if env is None:
                    variable = self._getVariable(expr)
                    #cvc_vars.update(variable.variables)
                    return variable.cvc_expr
                    #return variable
                else:
                    return env[expr.name]
            else:
                return self._astToCVCExpr(expr.expr, env)
    
        elif isinstance(expr, int) | isinstance(expr, str):
            if env is None:
                if isinstance(expr, int):
                    return CVCInteger.constant(expr, self.solver).cvc_expr
                elif isinstance(expr, str):
                    return CVCString.constant(expr, self.solver).cvc_expr
            else:
                return expr
    
        else:
            utils.crash("Unknown node during conversion from ast to CVC (expressions): %s" % expr)
    
