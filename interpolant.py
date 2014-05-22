from z3 import *

def sub_solver(level, alpha, solvers, interpolants):
     top = solvers[0]
     while(True):
          print "check"
          print level
          result = top.check(alpha)
          if (result == sat):
               if (len(solvers) == 1):
                   return True
               else:
                    model = top.model()
                    units = [ simplify(d() == model[d]) for d in model.decls() ]
                    print "units"
                    print units
                    sub_result = sub_solver(level+1,alpha + units, solvers[1:], interpolants[1:])
                    if (isinstance(sub_result,Z3PPObject)) :
                         print "learned"
                         print sub_result
                         top.add(sub_result)
                         interpolants[0].append(sub_result)
                    else:
                        return sub_result
          else:
               core = top.unsat_core()
               if (len(core) == 0):
                    return False
               else:
                    return simplify(Or([ Not(b) for b in core ]))

def assert_interpolants(formulas, interpolants):
     i = 0
     while(i<len(formulas)-1):
          s = Solver()
          interpolant = simplify(And(interpolants[i]))
          print "assert (no intersection)"
          check1 = And(formulas[i],interpolant)
          print check1
          s.add(check1)
          res = s.check()
          assert not(res == sat)
          print "assert (implication)"
          check2 = Not(Implies(formulas[i+1],simplify(interpolant)))
          print check2
          s.reset()
          s.add(check2)
          res = s.check()
          assert not(res == sat)
          # also need to check variables
          i = i + 1
               
def modular_sat_solver(formulas):
     print "modular_sat_solver"
     print formulas
     if len(formulas) == 0:
          return True
     else:
          pairup = [ (f,Solver()) for f in formulas ]
          interpolants = [ [] for f in formulas ]
          for fs in pairup:
               fs[1].add(fs[0])
          solvers = [ fs[1] for fs in pairup ]
          result = sub_solver( 0, [], solvers , interpolants)
          assert_interpolants(formulas, interpolants)
          return result     
          
b, c, d = Bools('b c d')
fA = And(b,Or(Not(b),c))
fB = And(Not(d),Or(Not(c),d))

example = [ fA, fB ]
final = modular_sat_solver(example)
print final

p, q, r, s = Bools('p q r s')
fA2 = Implies(Not(And(p,r)),And(Not(q),r))
fB2 = Not(Or(Implies(s,p),Implies(s,Not(q))))

print modular_sat_solver([fA2,fB2])

