from z3 import *

Char = BitVecSort(8)
List = Datatype('List')
List.declare('cons', ('head', Char), ('tail', List))
List.declare('nil')
List = List.create()

# abbreviations
cons = List.cons
head = List.head
tail = List.tail
nil = List.nil
Bool = BoolSort()

# don't use model-based quantifier instantiation here
set_param('smt.mbqi', False)
solver = SimpleSolver()

# we will set up axioms to solve for the regular expression [0-9]+|[a-z]

q0 = Function('q0',List,Bool)
q1 = Function('q1',List,Bool)
q2 = Function('q2',List,Bool)
q3 = Function('q3',List,Bool)
q4 = Function('q4',List,Bool)

y = Const('y',List)

def q0axiom():
	body = q0(y) == Or(q1(y),q3(y))
	return ForAll(y, body, patterns = [q0(y)])

def q1axiom():
	body = q1(y) == And(y!=nil,ULE(ord('0'),head(y)),ULE(head(y),ord('9')),q2(tail(y)))
	return ForAll(y, body, patterns = [q1(y)])

def q2axiom():
	body = q2(y) == Or(y==nil,And(y!=nil,ULE(ord('0'),head(y)),ULE(head(y),ord('9')),q2(tail(y))))
	return ForAll(y, body, patterns = [q2(y)])

def q3axiom():
	body = q3(y) == And(y!=nil,ULE(ord('a'),head(y)),ULE(head(y),ord('z')),q4(tail(y)))
	return ForAll(y, body, patterns = [q3(y)])

def q4axiom():
	body = q4(y) == (y==nil)
	return ForAll(y, body, patterns = [q4(y)])

#to generate longer results
def lengthGE(x,k):
  axiom = BoolVal(True)
  for i in range(k):
    axiom = And(axiom,Not(x == nil))
    x = tail(x)
  return axiom

def test():
  solver.add(q0axiom(),q1axiom(),q2axiom(),q3axiom(),q4axiom())
  y = Const('y',List)
  #solver.add(lengthGE(y,4))
  solver.add(q0(y))
  print(solver.assertions())
  ok = solver.check()
  assert(ok != unsat)
  print(solver.model())
  yVal = solver.model().evaluate(y,True)
  print(yVal)
  
test()
