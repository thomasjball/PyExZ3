#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
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

from bytecode_opcodes import ConditionalJump, Assignment, FunctionCall, ForLoop, ReturnValue, BuildList
from predicate import Predicate
from constraint import Constraint
import logging
import utils

log = logging.getLogger("se.interpret")

class SymbolicInterpreter:
	def __init__(self, engine):
		self.symbolic_variables = {}
		self.constraints = {}
		self.engine = engine
		self.root_constraint = Constraint(None, None)
		self.current_constraint = self.root_constraint
		self.branch_result_stack = []
		self.tracer = None

	def setTracer(self, tracer):
		self.tracer = tracer

	def whichBranch(self, branch):
		""" To be called from the process being executed, this function acts as instrumentation.
		branch can be either True or False, according to the branch taken after the last conditional
		jump. """
		if self.tracer.inside_tracing_code:
			return
		if len(self.branch_result_stack) > 0:
			stmt = self.branch_result_stack.pop()
			self.addBranchAfterJump(stmt, branch)
		else:
			utils.crash("Branch result without a conditional jump, problems with the whichBranch instrumentation")

	def addBranchAfterJump(self, stmt, result):
		if not stmt.isSymbolic():
			return

		p = Predicate(stmt, result)
		p.negate()
		cneg = self.current_constraint.findChild(p)
		p.negate()
		c = self.current_constraint.findChild(p)

		if c is None:
			c = self.current_constraint.addChild(p)
			self.engine.addConstraint(c)

		# Have we (accidentally) negated some constraint?
		# If yes, we can mark both as negated
		if cneg is not None:
			cneg.negated = True
			c.negated = True
			log.debug("Negated constraint: %s" % c)
		else:
			log.debug("New constraint: %s" % c)

		self.current_constraint = c

	def isStatementInteresting(self, stmt):
		if isinstance(stmt, ConditionalJump) and isinstance(stmt.condition, FunctionCall):
			utils.crash("Function call in if statement, broken instrumentation")
		elif isinstance(stmt, ConditionalJump):
			return True
		else:
			return stmt.isSymbolic()

	def newExecution(self):
		if len(self.branch_result_stack) > 0:
			log.error("One or more constraints were left without result during the previous execution")
			for s in self.branch_result_stack:
				log.error("--> " + str(s))
			raise KeyError
		self.current_constraint = self.root_constraint

	def symbolicExamine(self, stmt):
		# what kind of beast are we looking at here ?
		if isinstance(stmt, ConditionalJump): # A predicate !
			# The real work will be done after jump because we do not know
			# the taken branch yet
			self.branch_result_stack.append(stmt)
		elif isinstance(stmt, Assignment):
			pass
		elif isinstance(stmt, BuildList):
			pass
		elif isinstance(stmt, FunctionCall):
			pass
		elif isinstance(stmt, ForLoop):
			pass
		elif isinstance(stmt, ReturnValue):
			pass
		else:
			utils.crash("Unknown symbolic statement: %s" % repr(stmt))
		
		return

