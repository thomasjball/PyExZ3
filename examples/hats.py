from z3 import *

N = 7

# set up the bit vectors for the hats and what each person will guess
hat    = [ BitVec("Hat"+str(i),10) for i in range(N) ]
guess  = [ BitVec("Guess"+str(i),10) for i in range(N) ]

# compute the sum of each person i's guess and the hats numbers for all j != i
sum    = [ sum([guess[i]]+[ hat[j] for j in range(N) if j!=i]) for i in range(N) ]

# the program for each person i
prog   = [ (sum[i] % N) == i for i in range(N) ]

s = Solver()

def bounded(x):
	return And(0<=x,x<N)
s.add([ bounded(hat[i]) for i in range(N) ])
s.add([ bounded(guess[i]) for i in range(N) ])

s.add([ prog[i] for i in range(N) ])

# at least one person's guess is their own hat number
s.add(Not(Or([ guess[i] == hat[i] for i in range(N) ])))

print(s.check())
