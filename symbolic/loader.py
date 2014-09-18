# Copyright: copyright.txt

import inspect
import re
import os
import sys
from .invocation import FunctionInvocation
from .symbolic_types import SymbolicInteger

# TODO: we will need to generalize to allow user specification of symbolic types

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
			inv.addSymbolicParameter(a, lambda n,v : SymbolicInteger(n,v))
		return inv

	def reset_callback(self,firstpass=False):
		self.app = None
		if firstpass and self.test_name in sys.modules:
			print("There already is a module loaded named " + self.test_name)
			raise ImportError()
		try:
			if (not firstpass and self.test_name in sys.modules):
				del(sys.modules[self.test_name])
			self.app =__import__(self.test_name)
			if not self.test_name in self.app.__dict__ or not callable(self.app.__dict__[self.test_name]):
				print("File " +  self.test_name + ".py doesn't contain a function named " + self.test_name)
				raise ImportError()
		except Exception as arg:
			print("Couldn't import " + self.test_name)
			print(arg)
			raise ImportError()

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

	def check(self, computed, expected, as_bag=True):
		b_c = self.to_bag(computed)
		b_e = self.to_bag(expected)
		if as_bag and b_c != b_e or not as_bag and set(computed) != set(expected):
			print("-------------------> %s test failed <---------------------" % self.test_name)
			print("Expected: %s, found: %s" % (b_e, b_c))
			return False
		else:
			print("%s test passed <---" % self.test_name)
			return True

	def execution_complete(self, return_vals):
		if "expected_result" in self.app.__dict__:
			print(return_vals)
			return self.check(return_vals, self.app.__dict__["expected_result"]())
		if "expected_result_set" in self.app.__dict__:
			print(return_vals)
			return self.check(return_vals, self.app.__dict__["expected_result_set"](),False)
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
	except ImportError:
		sys.path = sys.path[1:]
		return None


