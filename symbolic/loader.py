#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
# To this file contributed: Peter Peresini
#
# Updated by Thomas Ball (2014) to make a generic test runner and harden against user error.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   -  Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   -  Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#   -  Neither the names of the contributors, nor their associated universities or
#      organizations may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import inspect
import re
import os
import sys
from symbolic.invocation import FunctionInvocation
from symbolic.symbolic_types.integers import SymbolicInteger

symbolic_vars = {}
	
def newInteger(name):
	if name not in symbolic_vars.keys():
		symbolic_vars[name] = SymbolicInteger(name,32)
	return symbolic_vars[name]

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
			inv.addSymbolicParameter(a, a, newInteger)
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
		except Exception(arg):
			print("Couldn't import " + self.test_name)
			print(arg)
			raise KeyError()

	def execute(self, **args):
		return self.app.__dict__[self.test_name](**args)

	def check(self, computed, expected):
		if len(computed) != len(expected) or computed != expected:
			print("-------------------> %s test failed <---------------------" % self.test_name)
			print("Expected: %s, found: %s" % (expected, computed))
			return False
		else:
			print("%s test passed <---" % self.test_name)
			return True

	def execution_complete(self, return_vals):
		if "expected_result" in self.app.__dict__:
			res = map(lambda x: x[0], return_vals)
			res.sort()
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
		sys.path = sys.path[1:]
		return ret
	except KeyError:
		sys.path = sys.path[1:]
		return None


