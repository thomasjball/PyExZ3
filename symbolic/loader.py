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
		self._testName = os.path.basename(filename)
		self._testName = self._testName[:-3]
		self._resetCallback(True)

	def getName(self):
		return self._testName
	
	def createInvocation(self):
		inv = FunctionInvocation(self._execute,self._resetCallback)
		func = self.app.__dict__[self._testName]
		# check to see if user specified initial values of arguments
		if "concrete_args" in func.__dict__:
			#TODO
			pass
		if "symbolic_args" in func.__dict__:
			#TODO: base on the type of the arg, find the appropriate
			#symbolic type and initialize it
			pass
		#TODO: make sure lists don't overlap and are included inside argspec.args
		argspec = inspect.getargspec(func)
		for a in argspec.args:
			inv.addSymbolicParameter(a, lambda n,v : SymbolicInteger(n,v))
		return inv

	def executionComplete(self, return_vals):
		if "expected_result" in self.app.__dict__:
			print(return_vals)
			return self._check(return_vals, self.app.__dict__["expected_result"]())
		if "expected_result_set" in self.app.__dict__:
			print(return_vals)
			return self._check(return_vals, self.app.__dict__["expected_result_set"](),False)
		else:
			print(self._testName + ".py contains no expected_result function")
			return None

	# -- private

	def _resetCallback(self,firstpass=False):
		self.app = None
		if firstpass and self._testName in sys.modules:
			print("There already is a module loaded named " + self._testName)
			raise ImportError()
		try:
			if (not firstpass and self._testName in sys.modules):
				del(sys.modules[self._testName])
			self.app =__import__(self._testName)
			if not self._testName in self.app.__dict__ or not callable(self.app.__dict__[self._testName]):
				print("File " +  self._testName + ".py doesn't contain a function named " + self._testName)
				raise ImportError()
		except Exception as arg:
			print("Couldn't import " + self._testName)
			print(arg)
			raise ImportError()

	def _execute(self, **args):
		return self.app.__dict__[self._testName](**args)

	def _toBag(self,l):
		bag = {}
		for i in l:
			if i in bag:
				bag[i] += 1
			else:
				bag[i] = 1
		return bag

	def _check(self, computed, expected, as_bag=True):
		b_c = self._toBag(computed)
		b_e = self._toBag(expected)
		if as_bag and b_c != b_e or not as_bag and set(computed) != set(expected):
			print("-------------------> %s test failed <---------------------" % self._testName)
			print("Expected: %s, found: %s" % (b_e, b_c))
			return False
		else:
			print("%s test passed <---" % self._testName)
			return True
	
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


