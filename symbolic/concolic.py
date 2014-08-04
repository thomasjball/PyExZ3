# Copyright: see copyright.txt

from collections import deque
import logging
import os
from stats import getStats

from .z3_wrap import Z3Wrapper
from .path_to_constraint import PathToConstraint
from .invocation import FunctionInvocation
from .symbolic_types import symbolic_type

log = logging.getLogger("se.conc")
stats = getStats()

class ConcolicEngine:
	def __init__(self, funcinv, reset, options):
		self.invocation = funcinv
		self.reset_func = reset
		self.options = options
		self.constraints_to_solve = deque([])
		self.num_processed_constraints = 0
		self.path = PathToConstraint(self)
		symbolic_type.SI = self.path
		self.execution_return_values = []
		stats.newCounter("explored paths")
		self.generated_inputs = []
		self.solver = Z3Wrapper()

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
		stats.incCounter("explored paths")
		self.reset_func()
		stats.pushProfile("single invocation")
		res = invocation.function(**invocation.symbolic_inputs)
		stats.popProfile()
		log.info("Invocation end")
		return res

	def record_inputs(self):
		concr_inputs = {}
		for k in self.invocation.symbolic_inputs:
			concr_inputs[k] = self.invocation.symbolic_inputs[k].getConcrValue()
		self.generated_inputs.append(concr_inputs)
		print(concr_inputs)
		
	def one_execution(self,expected_path=None):
		self.record_inputs()
		self.path.reset(expected_path)
		ret = self.execute(self.invocation)
		print(ret)
		self.execution_return_values.append(ret)

	def run(self, max_iterations=0):
		self.one_execution()
		
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
			model = selected.processConstraint(self.solver)
			stats.popProfile()

			if model == None:
				log.warning("Unsolvable constraints, skipping iteration")
				iterations += 1
				continue
			else:
				for name in model.keys():
					self.invocation.updateSymbolicParameter(name,model[name])

			self.one_execution(selected)

			iterations += 1			
			self.num_processed_constraints += 1

			if max_iterations != 0 and iterations >= max_iterations:
				log.debug("Maximum number of iterations reached, terminating")
				break

		if (self.options.dot_graph):
			file = open(self.options.filename+".dot","w")
			file.write(self.path.toDot())
			file.close()

		return self.execution_return_values
