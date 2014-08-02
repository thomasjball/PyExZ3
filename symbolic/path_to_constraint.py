# Copyright: see copyright.txt

import logging
import utils

from .predicate import Predicate
from .constraint import Constraint

log = logging.getLogger("se.pathconstraint")

class PathToConstraint:
	def __init__(self, engine):
		self.constraints = {}
		self.engine = engine
		self.root_constraint = Constraint(None, None)
		self.current_constraint = self.root_constraint
		self.expected_path = None

	def reset(self,expected):
		self.current_constraint = self.root_constraint
		if expected==None:
			self.expected_path = None
		else:
			self.expected_path = []
			tmp = expected
			while tmp.predicate is not None:
				self.expected_path.append(tmp.predicate)
				tmp = tmp.parent

	def whichBranch(self, branch, cond_expr):
		""" To be called from the process being executed, this function acts as instrumentation.
		branch can be either True or False, according to the branch taken after the last conditional
		jump. """

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
			# check for path mismatch
			if self.expected_path != None and self.expected_path != []:
				expected = self.expected_path.pop()
				if (not expected.expr.symbolicEq(c.predicate.expr) or expected.result == c.predicate.result):
					print("Replay mismatch")
					print(expected)
					print(c.predicate)
		else:
			# check for path mismatch
			if self.expected_path != None and self.expected_path != []:
				expected = self.expected_path.pop()
				if (c.predicate != expected):
					print("Replay mismatch")
					print(expected)
					print(c.predicate)

		if cneg is not None:
			# We've already processed both
			cneg.processed = True
			c.processed = True
			log.debug("Processed constraint: %s" % c)

		self.current_constraint = c

	def toDot(self):
		# print the thing into DOT format
		header = "digraph {\n"
		footer = "\n}\n"
		return header + self._toDot(self.root_constraint) + footer

	def _toDot(self,c):
		if (c.parent == None):
			label = "root"
		else:
			label = c.predicate.expr.toString()
			if not c.predicate.result:
				label = "Not("+label+")"
		node = "C" + str(c.id) + " [ label=\"" + label + "\" ];\n"
		edges = [ "C" + str(c.id) + " -> " + "C" + str(child.id) + ";\n" for child in c.children ]
		return node + "".join(edges) + "".join([ self._toDot(child) for child in c.children ])
		
