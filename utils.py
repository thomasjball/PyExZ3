# Copyright: see copyright.txt

import sys
import traceback

def _traceback():
	stack = traceback.format_stack()
	return stack[:-2]

def crash(msg):
	stack = _traceback()
	print("\n"+"".join(stack))
	print(msg)
	sys.exit(-1)
