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

	def reset(self):
		self.current_constraint = self.root_constraint

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
		
