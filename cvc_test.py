__author__ = 'Peter'

from CVC4 import ExprManager, SmtEngine, SExpr, Rational
import CVC4
em = ExprManager()
solver = SmtEngine(em)
solver.setOption("produce-models", SExpr("true"))
print(solver.getOption("incremental").toString())
print(solver.getOption("produce-models").toString())
a = em.mkVar("a", em.integerType())
b = em.mkVar("b", em.integerType())
ite = em.mkExpr(CVC4.ITE, em.mkExpr(CVC4.EQUAL, a, b), em.mkConst(Rational(1)), em.mkConst(Rational(0)))
solver.assertFormula(em.mkExpr(CVC4.EQUAL, ite, em.mkConst(0)))
result = solver.checkSat()
print(result.toString())
print(solver.getValue(a).toString())
print(solver.getValue(b).toString())
