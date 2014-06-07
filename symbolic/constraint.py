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

import symbolic.z3_wrap as z3_mod
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

	def negateConstraint(self):
		# We want to mark this as processed even in case of error
		# so it is best to do it at the beginning
		self.processed = True
		res = False
		sym_asserts = []
		sym_vars = {}

		tmp = self.parent
		while tmp.predicate is not None:
			p = tmp.predicate
			(ret, expr) = p.buildZ3Expr()
			res |= ret
			if ret:
				sym_asserts.append(expr)
				for v in p.sym_vars:
					sym_vars[v] = p.sym_vars[v]
			tmp = tmp.parent

		(ret, expr) = self.predicate.buildZ3Expr()
		if expr is None:
			# We are not able to fix the last branch
			return False
		if ret:
			for v in self.predicate.sym_vars:
				sym_vars[v] = self.predicate.sym_vars[v]
		res |= ret
		new_values = z3_mod.findCounterexample(sym_asserts, expr, sym_vars)
		if new_values != None:
			for (var, instance, new_val) in new_values:
				instance.setConcrValue(new_val)
				log.info("Assigning concrete value %s to symbolic variable %s" % (str(instance.getConcrValue()), var))
		else:
			return False
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
		"""returns constraint by addition of predicate to this constraint"""
		assert(self.findChild(predicate) is None)
		c = Constraint(self, predicate)
		self.children.append(c)
		return c
