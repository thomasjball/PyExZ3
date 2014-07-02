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

log = logging.getLogger("se.constraint")

class Constraint:
	"""A constraint is a list of predicates leading to some specific
	   position in the code."""
	def __init__(self, parent, last_predicate):
		self.predicate = last_predicate
		self.processed = False
		self.parent = parent
		self.children = []

	def __eq__(self, other):
		"""Two Constraints are equal iff they have the same chain of predicates"""
		if isinstance(other, Constraint):
			if not self.predicate == other.predicate:
				return False
			return self.parent is other.parent
		else:
			return False

	def processConstraint(self):
		self.processed = True

		# collect the assertions
		sym_asserts = []
		tmp = self.parent
		while tmp.predicate is not None:
			sym_asserts.append(tmp.predicate.buildBooleanExpr())
			tmp = tmp.parent

		# get the final expression (which will be negated)
		expr = self.predicate.buildBooleanExpr()

		# ask the constraint solver for new input
		new_values = self.predicate.solver.findCounterexample(sym_asserts, expr)

		res = []
		if new_values != None:
			res = new_values
		
		return res

	def getLength(self):
		if self.parent == None:
			return 0
		return 1 + self.parent.getLength()

	def __str__(self):
		return str(self.predicate) + "  (processed: %s, path_len: %d)" % (self.processed,self.getLength())

	def __repr__(self):
		s = repr(self.predicate) + " (processed: %s)" % (self.processed)
		if self.parent is not None:
			s += "\n  path: %s" % repr(self.parent)
		return s

	def findChild(self, predicate):
		for c in self.children:
			if predicate == c.predicate:
				return c
		return None

	def addChild(self, predicate):
		assert(self.findChild(predicate) is None)
		c = Constraint(self, predicate)
		self.children.append(c)
		return c
