from z3 import *

x = BitVec("x",8)
y = BitVec("y",8)
z = BitVec("z",8)

s = Solver()
s.add(x > 0,y > 0,z==x+y)
s.add(Not(z > 0))

result = s.check()
if result == sat:
	print(s.model())
else:
	print(result)

