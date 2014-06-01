#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
# To this file contributed: Peter Peresini
#
# Updated by Thomas Ball (2014)
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
#

from symbolic import invocation
from symbolic.symbolic_types.symbolic_store import newInteger
import inspect

# Do not import you packages here, but do it in the callbacks below.
# Otherwise the application will run with non-instrumented versions of those modules.

TESTS = ["many_branches", "shallow_branches", "loop", "hashval", "logical_op", "elseif", "dictionary", "expressions"] 

# TODO: make TESTS a funcion of .py in the test directory except for this file
# TODO: harden this class against errors to help users get set up correctly with new tests

class SymExecApp:
	APP_NAME="SE regression test suite"
	# list of single modules (filenames with relative path from current dir) to normalize
	NORMALIZE_MODS = [ t + ".py" for t in TESTS ]
	# As above, but for packages. The normalization will be recursive and cover the full package
	NORMALIZE_PACKAGES = [] 

	def __init__(self, which_test):
		# TBALL: do the import here and fail if import doesn't work
		if which_test in TESTS:
			self.test_name = which_test
		else:
			print "No test specified"
		self.reset_callback()

	def create_invocations(self):
		invocation_sequence = []
		inv = invocation.FunctionInvocation(self.execute)
		func = self.app.__dict__[self.test_name]
		# TODO: it should be a function
		# TODO: find number of arguments
		argspec = inspect.getargspec(func)
		for a in argspec.args:
			inv.addSymbolicParameter(a, a, newInteger)
		invocation_sequence.append(inv)
		return invocation_sequence

	def reset_callback(self):
		# TBALL: handle import of missing module
		self.app =__import__(self.test_name)

	def execute(self, **args):
		# TBALL: does test_name exist in app?
		return self.app.__dict__[self.test_name](**args)

	def check(self, computed, expected):
		if len(computed) != len(expected) or computed != expected:
			print "-------------------> %s test failed <---------------------" % self.test_name
			print "Expected: %s, found: %s" % (expected, computed)
		else:
			print "%s test passed <---" % self.test_name

	def execution_complete(self, return_vals):
		res = map(lambda x: x[0], return_vals)
		res.sort()
		self.check(res, self.app.__dict__["expected_result"]())

	
def factory(param):
	# TBALL: need to check parameter is there!
	return SymExecApp(param[0])

