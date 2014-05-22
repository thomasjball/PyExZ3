#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
# To this file contributed: Peter Peresini
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
# Do not import you packages here, but do it in the callbacks below.
# Otherwise the application will run with non-instrumented versions of those modules.

class SymExecApp:
	APP_NAME="SE regression test suite"
	NORMALIZE_MODS = ["many_branches.py", "shallow_branches.py", "loop.py",
			"logical_op.py", "elseif.py", "dictionary.py", "count_packets.py",
			"expressions.py"] # list of single modules (filenames with relative path from current dir) to normalize
	NORMALIZE_PACKAGES = [] # As above, but for packages. The normalization will be recursive and cover the full package
	USES_NOX_API = True # This will cause the NOX SE library to be instrumented and copied in the import PATH

	def __init__(self, which_test):
		if which_test == "many_branches":
			self.test_name = "many_branches"
		elif which_test == "shallow_branches":
			self.test_name = "shallow_branches"
		elif which_test == "loop":
			self.test_name = "loop"
		elif which_test == "logical_op":
			self.test_name = "logical_op"
		elif which_test == "elif":
			self.test_name = "elif"
		elif which_test == "dictionary":
			self.test_name = "dictionary"
		elif which_test == "count_packets":
			self.test_name = "count_packets"
		elif which_test == "expressions":
			self.test_name = "expressions"
		else:
			print "No test specified"
		self.app = None

	def create_invocations(self):
		invocation_sequence = []
		if self.test_name == "many_branches":
			inv = invocation.FunctionInvocation(self.run_many_branches)
			inv.addSymbolicParameter("in1", "in1", newInteger)
			inv.addSymbolicParameter("in2", "in2", newInteger)
			inv.addSymbolicParameter("in3", "in3", newInteger)
		elif self.test_name == "shallow_branches":
			inv = invocation.FunctionInvocation(self.run_shallow_branches)
			inv.addSymbolicParameter("in1", "in1", newInteger)
			inv.addSymbolicParameter("in2", "in2", newInteger)
			inv.addSymbolicParameter("in3", "in3", newInteger)
			inv.addSymbolicParameter("in4", "in4", newInteger)
			inv.addSymbolicParameter("in5", "in5", newInteger)
		elif self.test_name == "loop":
			inv = invocation.FunctionInvocation(self.run_loop)
			inv.addSymbolicParameter("in1", "in1", newInteger)
			inv.addSymbolicParameter("in2", "in2", newInteger)
		elif self.test_name == "logical_op":
			inv = invocation.FunctionInvocation(self.run_logical_op)
			inv.addSymbolicParameter("in1", "in1", newInteger)
			inv.addSymbolicParameter("in2", "in2", newInteger)
		elif self.test_name == "elif":
			inv = invocation.FunctionInvocation(self.run_elif)
			inv.addSymbolicParameter("in1", "in1", newInteger)
		elif self.test_name == "dictionary":
			inv = invocation.FunctionInvocation(self.run_dictionary)
			inv.addSymbolicParameter("in1", "in1", newInteger)
		elif self.test_name == "count_packets":
			from nox.lib.packet.ethernet import ethernet
			inv = invocation.FunctionInvocation(self.run_count_packets)
			inv.addParameter("cnt", {'lldp' : 0, 'normal' : 0})
			inv.addSymbolicParameter("packet", "packet", ethernet)
		elif self.test_name == "expressions":
			inv = invocation.FunctionInvocation(self.run_expressions)
			inv.addSymbolicParameter("in1", "in1", newInteger)
			inv.addSymbolicParameter("in2", "in2", newInteger)
		invocation_sequence.append(inv)
		return invocation_sequence

	def reset_callback(self):
		if self.test_name == "many_branches":
			self.app = __import__("many_branches")
		elif self.test_name == "shallow_branches":
			self.app = __import__("shallow_branches")
		elif self.test_name == "loop":
			self.app = __import__("loop")
		elif self.test_name == "logical_op":
			self.app = __import__("logical_op")
		elif self.test_name == "elif":
			self.app = __import__("elseif")
		elif self.test_name == "dictionary":
			self.app = __import__("dictionary")
		elif self.test_name == "count_packets":
			self.app = __import__("count_packets")
		elif self.test_name == "expressions":
			self.app = __import__("expressions")

	def run_shallow_branches(self, **args):
		return self.app.shallow_branches(**args)

	def run_many_branches(self, **args):
		return self.app.many_branches(**args)

	def run_loop(self, **args):
		return self.app.loop(**args)

	def run_logical_op(self, **args):
		return self.app.logical_op(**args)

	def run_elif(self, **args):
		return self.app.elseif(**args)

	def run_dictionary(self, **args):
		return self.app.dictionary(**args)

	def run_count_packets(self, **args):
		return self.app.packet_in_callback(**args)

	def run_expressions(self, **args):
		return self.app.expressions(**args)

	def check(self, computed, expected):
		if len(computed) != len(expected) or computed != expected:
			print "-------------------> %s test failed <---------------------" % self.test_name
			print "Expected: %s, found: %s" % (expected, computed)
		else:
			print "%s test passed <---" % self.test_name

	def execution_complete(self, return_vals):
		if self.test_name == "many_branches":
			res = map(lambda x: x[0], return_vals)
			res.sort()
			self.check(res, [1, 2, 3, 4, 5, 6, 7, 8])
		elif self.test_name == "shallow_branches":
			res = map(lambda x: x[0], return_vals)
			res.sort()
			self.check(res, [0, 1, 3, 5, 7, 9])
		elif self.test_name == "loop":
			res = map(lambda x: x[0], return_vals)
			res.sort()
			self.check(res, [0, 2, 2])
		elif self.test_name == "logical_op":
			res = map(lambda x: x[0], return_vals)
			res.sort()
			self.check(res, [2, 3])
		elif self.test_name == "elif":
			res = map(lambda x: x[0], return_vals)
			res.sort()
			self.check(res, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
		elif self.test_name == "dictionary":
			res = map(lambda x: x[0], return_vals)
			res.sort()
			self.check(res, [1, 2])
		elif self.test_name == "count_packets":
			res = map(lambda x: x[0], return_vals)
			self.check(res, [{'lldp': 1, 'normal': 1}, {'lldp': 1, 'normal': 1}])
		elif self.test_name == "count_packets":
			res = map(lambda x: x[0], return_vals)
			self.check(res, [{'lldp': 1, 'normal': 1}, {'lldp': 1, 'normal': 1}])
		elif self.test_name == "expressions":
			res = map(lambda x: x[0], return_vals)
			self.check(res, [0, -1, 0, 0])
		else:
			print "---------------------> Unknown test <-------------------"
	
def factory(param):
	# TBALL: need to check parameter is there!
	return SymExecApp(param[0])

