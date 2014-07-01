#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
#
# Updated by Thonas Ball (2014)
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
from .symbolic_types import SymbolicType

log = logging.getLogger("se.predicate")

class Predicate:
	"""Predicate is one specific ``if'' encountered during the program execution.
	   """
	def __init__(self, solver, condexpr, result):
		self.solver = solver
		self.expr = condexpr
		self.result = result

	def __eq__(self, other):
		if isinstance(other, Predicate):
			res = self.result == other.result and self.expr.symbolicEq(other.expr)
			return res
		else:
			return False

	def __hash__(self):
		return hash(self.expr)

	def __str__(self):
		return str(self.expr) + " (was %s)" % (self.result)

	def __repr__(self):
		return repr(self.expr) + " (was %s)" % (self.result)

	def getSymVariables(self):
		return self.expr.getSymVariables()

	def negate(self):
		"""Negates the current predicate"""
		assert(self.result is not None)
		self.result = not self.result

	def buildBooleanExpr(self):
		return self.solver.buildBooleanExpr(self.expr,self.result)

