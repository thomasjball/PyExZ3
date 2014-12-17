import logging

import CVC4
from symbolic.cvc_expr.expression import CVCExpression
from symbolic.cvc_expr.integer import CVCInteger
from symbolic.cvc_expr.string import CVCString
from symbolic.symbolic_types import SymbolicInteger, SymbolicStr
from symbolic.symbolic_types.symbolic_type import SymbolicObject
import utils

log = logging.getLogger("se.cvc_expr.exprbuilder")

cvc_vars = {}

def toCVC(asserts, query, solver):
    global cvc_vars
    cvc_vars = {}
    for p in asserts:
        solver.assertFormula(_predToCVC(p, solver).cvc_expr)
    cvc_query = _predToCVC(query, solver).not_op()
    log.debug("Querying solver for %s" % cvc_query)
    solver.assertFormula(cvc_query.cvc_expr)
    #return cvc_query.variables
    return cvc_vars

def _predToCVC(pred, solver, env=None):
    sym_expr = CVCExpression(_astToCVCExpr(pred.symtype, solver, env), solver, cvc_vars)
    log.debug("Converting predicate %s to CVC expression %s" % (pred, sym_expr))
    if env is None:
        if not sym_expr.cvc_expr.getType().isBoolean():
            sym_expr = (sym_expr == CVCInteger.constant(0, solver)).not_op()
        if not pred.result:
            sym_expr = sym_expr.not_op()
    else:
        if not pred.result:
            sym_expr = sym_expr.not_op()
    return sym_expr

# def _getVariable(symbolic_var, solver):
#     name = symbolic_var.name
#     variable = None
#     if isinstance(symbolic_var, SymbolicInteger):
#         variable = CVCInteger.variable(name, solver)
#     elif isinstance(symbolic_var, SymbolicStr):
#         variable = CVCString.variable(name, solver)
#     return variable

def _getVariable(expr, solver):
    name = expr.name
    if name not in cvc_vars:
        variable = None
        if isinstance(expr, SymbolicInteger):
            variable = CVCInteger.variable(name, solver).cvc_expr
        elif isinstance(expr, SymbolicStr):
            variable = CVCString.variable(name, solver).cvc_expr
        cvc_vars[name] = variable
    return cvc_vars[name]


def _wrapIf(expr, solver, env):
    em = solver.getExprManager()
    if env is None:
        return em.mkExpr(CVC4.ITE, expr, CVCInteger.constant(1, solver).cvc_expr, CVCInteger.constant(0, solver).cvc_expr)
    else:
        return expr


#def _wrapIf(expr, solver, env):
#    if env is None:
#        return CVCExpression(expr, solver).ite(CVCInteger.constant(1, solver), CVCInteger.constant(0, solver)).cvc_expr
#    else:
#        return expr

def _astToCVCExpr(expr, solver, env=None):
    global cvc_vars
    em = solver.getExprManager()

    log.debug("Converting %s (type: %s) to CVC expression" % (expr, type(expr)))
    if isinstance(expr, list):
        op = expr[0]
        args = [_astToCVCExpr(a, solver, env) for a in expr[1:]]
        cvc_l, cvc_r = args[0], args[1]
        log.debug("Building %s %s %s" % (cvc_l.toString(), op, cvc_r.toString()))

        optype = None

        if cvc_l.getType().isInteger() or cvc_l.getType().isReal():
            optype = CVCInteger(None, solver)
        elif cvc_l.getType().isString():
            optype = CVCString(None, solver)
        else:
            utils.crash("Unknown operand type during conversion from ast to CVC (expressions): %s" % cvc_l.getType().toString())

        # arithmetical operations
        if op == "+":
            return optype.add(cvc_l, cvc_r, solver)
        elif op == "-":
            return optype.sub(cvc_l, cvc_r, solver)
        elif op == "*":
            return optype.mul(cvc_l, cvc_r, solver)
        elif op == "//":
            return optype.div(cvc_l, cvc_r, solver)
        elif op == "%":
            return optype.mod(cvc_l, cvc_r, solver)

        # bitwise
        elif op == "<<":
            return optype.lsh(cvc_l, cvc_r, solver)
        elif op == ">>":
            return optype.rsh(cvc_l, cvc_r, solver)
        elif op == "^":
            return optype.xor(cvc_l, cvc_r, solver)
        elif op == "|":
            return optype.orop(cvc_l, cvc_r, solver)
        elif op == "&":
            return optype.andop(cvc_l, cvc_r, solver)

        # equality gets coerced to integer
        elif op == "==":
            return _wrapIf(em.mkExpr(CVC4.EQUAL, cvc_l, cvc_r), solver, env)
        elif op == "!=":
            return _wrapIf(em.mkExpr(CVC4.NOT, em.mkExpr(CVC4.EQUAL, cvc_l, cvc_r)), solver, env)
        elif op == "<":
            return _wrapIf(em.mkExpr(CVC4.LT, cvc_l, cvc_r), solver, env)
        elif op == ">":
            return _wrapIf(em.mkExpr(CVC4.GT, cvc_l, cvc_r), solver, env)
        elif op == "<=":
            return _wrapIf(em.mkExpr(CVC4.LEQ, cvc_l, cvc_r), solver, env)
        elif op == ">=":
            return _wrapIf(em.mkExpr(CVC4.GEQ, cvc_l, cvc_r), solver, env)
        else:
            utils.crash("Unknown BinOp during conversion from ast to CVC (expressions): %s" % op)

    elif isinstance(expr, SymbolicObject):
        if expr.isVariable():
            if env is None:
                variable = _getVariable(expr, solver)
                #cvc_vars = dict(cvc_vars, **variable.variables)
                #return variable.cvc_expr
                return variable
            else:
                return env[expr.name]
        else:
            return _astToCVCExpr(expr.expr, solver, env)

    elif isinstance(expr, int) | isinstance(expr, str):
        if env is None:
            if isinstance(expr, int):
                return CVCInteger.constant(expr, solver).cvc_expr
            elif isinstance(expr, str):
                return CVCString.constant(expr, solver).cvc_expr
        else:
            return expr

    else:
        utils.crash("Unknown node during conversion from ast to CVC (expressions): %s" % expr)