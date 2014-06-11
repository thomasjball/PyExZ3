# Modification of diamond.py, which cleans up state by deleting variables that
# are no longer used. This allows for state subsumption checking to succeed.

# This test should fail with --cutting

def cut_diamond(a,b,c):
	ret = 0
	if (a):
		ret = ret + 1
	del a
	if (b):
		ret = ret + 1
	del b
	if (c):
		ret = ret + 1
	del c
	return ret

def expected_result():
	return [ 0, 1, 1, 1, 2, 2, 2, 3]