# Copyright: copyright.txt

import inspect
import re
import os
import sys
from .invocation import FunctionInvocation
from .symbolic_types import SymbolicInteger

def newInteger(name,val):
	return SymbolicInteger(name,val)

class Loader:
	def __init__(self, filename):
		self.test_name = os.path.basename(filename)
		self.test_name = self.test_name[:-3]
		self.reset_callback(True)

	def create_invocation(self):
		inv = FunctionInvocation(self.execute)
		# associate a SymbolicInteger with each formal parameter of function
		func = self.app.__dict__[self.test_name]
		argspec = inspect.getargspec(func)
		for a in argspec.args:
			inv.addSymbolicParameter(a, newInteger, 0)
		return inv

	def reset_callback(self,firstpass=False):
		self.app = None
		if firstpass and self.test_name in sys.modules:
			print("There already is a module loaded named " + self.test_name)
			raise KeyError()
		try:
			if (not firstpass and self.test_name in sys.modules):
				del(sys.modules[self.test_name])
			self.app =__import__(self.test_name)
			if not self.test_name in self.app.__dict__:
				print(which_test + ".py doesn't contain a function named " + which_test)
				raise KeyError()
			# TODO: check that we have a function
		except Exception as arg:
			print("Couldn't import " + self.test_name)
			print(arg)
			raise KeyError()

	def execute(self, **args):
		return self.app.__dict__[self.test_name](**args)

	def to_bag(self,l):
		bag = {}
		for i in l:
			if i in bag:
				bag[i] += 1
			else:
				bag[i] = 1
		return bag

	def check(self, computed, expected):
		b_c = self.to_bag(computed)
		b_e = self.to_bag(expected)
		print(b_c)
		print(b_e)
		if len(computed) != len(expected) or b_c != b_e:
			print("-------------------> %s test failed <---------------------" % self.test_name)
			print("Expected: %s, found: %s" % (b_e, b_c))
			return False
		else:
			print("%s test passed <---" % self.test_name)
			return True

	def execution_complete(self, return_vals):
		if "expected_result" in self.app.__dict__:
			res = [ x[0] for x in return_vals ]
			return self.check(res, self.app.__dict__["expected_result"]())
		else:
			print(self.test_name + ".py contains no expected_result function")
			return None
	
def loaderFactory(filename):
	if not os.path.isfile(filename) or not re.search(".py$",filename):
		print("Please provide a Python file to load")
		return None
	try: 
		dir = os.path.dirname(filename)
		sys.path = [ dir ] + sys.path
		ret = Loader(filename)
		return ret
	except KeyError:
		sys.path = sys.path[1:]
		return None


