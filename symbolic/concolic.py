# Copyright: see copyright.txt

from collections import deque
import logging
import os

from .z3_wrap import Z3Wrapper
from .path_to_constraint import PathToConstraint
from .invocation import FunctionInvocation
from .symbolic_types import symbolic_type

log = logging.getLogger("se.conc")

class ConcolicEngine:
	def __init__(self, funcinv):
		self.invocation = funcinv
		# the input to the function
		self.symbolic_inputs = {}  # string -> SymbolicType
		# TODO: we need to get default values from the type instead
		for n in funcinv.getNames():
			self.symbolic_inputs[n] = funcinv.createParameterValue(n,0)

		self.constraints_to_solve = deque([])
		self.num_processed_constraints = 0

		self.path = PathToConstraint(self)
		# link up SymbolicType to PathToConstraint in order to intercept control-flow
		symbolic_type.SymbolicType.SI = self.path

		self.solver = Z3Wrapper()

		# outputs
		self.generated_inputs = []
		self.execution_return_values = []

	def updateSymbolicParameter(self, name, val):
		self.symbolic_inputs[name] = self.invocation.createParameterValue(name,val)

	def getInputs(self):
		# TODOthis could be optimized
		return self.symbolic_inputs.copy()

	def setInputs(self,d):
		self.symbolic_inputs = d

	def addConstraint(self, constraint):
		self.constraints_to_solve.append(constraint)
		# make sure to remember the input that led to this constraint
		constraint.inputs = self.getInputs()

	def isExplorationComplete(self):
		num_constr = len(self.constraints_to_solve)
		if num_constr == 0:
			log.info("Exploration complete")
			return True
		else:
			log.info("%d constraints yet to solve (total: %d, already solved: %d)" % (num_constr, self.num_processed_constraints + num_constr, self.num_processed_constraints))
			return False

	def execute(self, invocation):
		res = invocation.callFunction(self.symbolic_inputs)
		return res

	def record_inputs(self):
		args = self.symbolic_inputs
		inputs = [ (k,args[k].getConcrValue()) for k in args ]
		self.generated_inputs.append(inputs)
		print(inputs)
		
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
			self.setInputs(selected.inputs)			

			log.info("Selected constraint %s" % selected)
			model = selected.processConstraint(self.solver)

			if model == None:
				continue
			else:
				for name in model.keys():
					self.updateSymbolicParameter(name,model[name])

			self.one_execution(selected)

			iterations += 1			
			self.num_processed_constraints += 1

			if max_iterations != 0 and iterations >= max_iterations:
				log.info("Maximum number of iterations reached, terminating")
				break

		return (self.execution_return_values,self.path)
