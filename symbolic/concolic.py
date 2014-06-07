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


from path_to_constraint import PathToConstraint
from symbolic import instrumentation
from collections import deque
import logging
from stats import getStats

log = logging.getLogger("se.conc")
stats = getStats()

class ConcolicEngine:
	def __init__(self, funcinv, debug):
		self.invocation = funcinv
		self.constraints_to_solve = deque([])
		self.num_processed_constraints = 0
		self.path = PathToConstraint(self)
		instrumentation.SI = self.path
		self.execution_return_values = []
		self.reset_func = None
		self.tracer = None # PythonTracer(debug)
		# self.tracer.setInterpreter(self.path)
		# self.path.setTracer(self.tracer)
		stats.newCounter("explored paths")
		self.generated_inputs = []

	def setResetCallback(self, reset_func):
		self.reset_func = reset_func

	def addConstraint(self, constraint):
		self.constraints_to_solve.append(constraint)

	def isExplorationComplete(self):
		num_constr = len(self.constraints_to_solve)
		if num_constr == 0:
			log.info("Exploration complete")
			return True
		else:
			log.info("%d constraints yet to solve (total: %d, already solved: %d)" % (num_constr, self.num_processed_constraints + num_constr, self.num_processed_constraints))
			return False

	def execute(self, invocation):
		return_values = []
		stats.incCounter("explored paths")
		log.info("Iteration start")
		stats.pushProfile("single iteration")
		self.reset_func()
		
		# invocation.setupTracer(self.tracer)
		stats.pushProfile("single invocation")
		# res = self.tracer.execute()
		res = invocation.function(**invocation.symbolic_inputs)
		stats.popProfile()
		return_values.append(res)
		log.info("Invocation end")
		stats.popProfile()
		log.info("Iteration end")
		return return_values

	def record_inputs(self):
		concr_inputs = {}
		for k in self.invocation.symbolic_inputs:
			concr_inputs[k] = self.invocation.symbolic_inputs[k].getConcrValue()
		self.generated_inputs.append(concr_inputs)
		
	def run(self, max_iterations=0):
		self.record_inputs()
		self.path.reset()
		ret = self.execute(self.invocation)
		self.execution_return_values.append(ret)

		iterations = 1
		if max_iterations != 0 and iterations >= max_iterations:
			log.debug("Maximum number of iterations reached, terminating")
			return self.execution_return_values

		while not self.isExplorationComplete():
			selected = self.constraints_to_solve.popleft()
			if selected.processed:
				continue

			log.info("Solving constraint %s" % selected)
			stats.pushProfile("constraint solving")
			ret = selected.negateConstraint()
			stats.popProfile()

			if not ret:
				log.warning("Unsolvable constraints, skipping iteration")
				iterations += 1
				continue

			self.record_inputs()	
			self.path.reset()
			ret = self.execute(self.invocation)
			self.execution_return_values.append(ret)

			iterations += 1			
			self.num_processed_constraints += 1

			if max_iterations != 0 and iterations >= max_iterations:
				log.debug("Maximum number of iterations reached, terminating")
				break

		return self.execution_return_values

