#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
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

import symbolic.z3_wrap as z3_wrap
from symbolic_types import SymbolicType, SymbolicInteger
from predicate import Predicate
from constraint import Constraint
import logging
from stats import getStats
import utils
import inspect
import copy
from z3 import *

class EndExecutionThrowable: pass

log = logging.getLogger("se.pathconstraint")
stats = getStats()

class PathToConstraint:
	def __init__(self, engine):
		self.symbolic_variables = {}
		self.constraints = {}
		self.engine = engine
		self.root_constraint = Constraint(None, None)
		self.current_constraint = self.root_constraint
		self.target_reached = False

	def reset(self):
		self.current_constraint = self.root_constraint
		self.target_reached = False

	def whichBranch(self, branch, cond_expr):
		""" To be called from the process being executed, this function acts as instrumentation.
		branch can be either True or False, according to the branch taken after the last conditional
		jump. """

		if not (isinstance(cond_expr,SymbolicType)):
			return

		if self.engine.cutting:
			stats.pushProfile("subsumption checking")
			# Important: this call may jump out of this function (and the
			# whole execution) by throwing an EndExecutionThrowable
			self.tryCut()
			stats.popProfile()

		# add both possible predicate outcomes to constraint (tree)
		p = Predicate(cond_expr, branch)
		p.negate()
		cneg = self.current_constraint.findChild(p)
		p.negate()
		c = self.current_constraint.findChild(p)

		if c is None:
			c = self.current_constraint.addChild(p)
			# Important: we are adding the new constraint
			# to the queue of the engine for later processing
			log.debug("New constraint: %s" % c)
			self.engine.addConstraint(c)

		if cneg is not None:
			# We've already processed both
			cneg.processed = True
			c.processed = True
			log.debug("Processed constraint: %s" % c)

		self.current_constraint = c

		if not self.engine.selected or self.engine.selected is cneg:
			self.target_reached = True

	def tryCut(self):
		if not self.target_reached:
			return

		# Check that this whichBranch call was made from the top level function in the program
		# under test.
		# TODO: add recording of state from multiple function frames to remove this limitation
		caller_of_instrumented = inspect.getouterframes(inspect.currentframe())[4][3] # function name
		if not caller_of_instrumented == "execute":
			log.debug("Skip subsumption checking due to not being in top level function")
			return

		(frame, filename, line_number, function_name, lines, line_index) = inspect.getouterframes(
			inspect.currentframe())[3]
		pc = filename + ":" + str(line_number)

		state = dict(frame.f_locals)
		state.pop("__se_cond__", None) # remove __se_cond__ because  it is never reused

		# check for subsumption
		for (old_state, old_constraint) in self.engine.states[pc]:
			if self.isSubsumed(state, old_state, old_constraint):
				log.debug("State subsumed: %s contained in %s" % (self.current_constraint, old_constraint))
				stats.incCounter("paths cut")
				raise EndExecutionThrowable()

		# was not subsumed by anything, record state
		self.engine.states[pc].append((state, self.current_constraint))

	def isSubsumed(self, my_state, old_state, old_constraint):
		if not set(my_state) == set(old_state):
			return

		my_concretes = {k: v for k, v in my_state.iteritems() if not isinstance(v, SymbolicType)}
		old_concretes = {k: v for k, v in old_state.iteritems() if not isinstance(v, SymbolicType)}
		# all purely concrete variables must be equal
		for var in my_concretes.viewkeys() & old_concretes.viewkeys():
			if my_concretes[var] != old_concretes[var]:
				return

		# assert that the states must be equal
		my_constraint = self.current_constraint
		state_vars = set()
		for var in set(my_state):
			# use a variable name that is illegal in python
			state_var = var + "$"
			state_sym_var = SymbolicInteger(state_var, 32)
			state_vars.add(state_var)
			my_p = Predicate(state_sym_var == my_state[var], True)
			my_constraint = Constraint(my_constraint, my_p)
			old_p = Predicate(state_sym_var == old_state[var], True)
			old_constraint = Constraint(old_constraint, old_p)

		(_, my_asserts, _) = my_constraint.buildZ3Asserts()
		(_, old_asserts, old_sym_vars) = old_constraint.buildZ3Asserts()
		old_inputs = [v[1] for k, v in old_sym_vars.iteritems() if not k in state_vars]

		subsumed = Implies(And(my_asserts), Exists(old_inputs, And(old_asserts)))
		return z3_wrap.findCounterexample([], subsumed, []) == None
