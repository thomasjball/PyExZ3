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

from symbolic_type import SymbolicType
import symbolic.z3_wrap as wrap

class SymbolicInteger(SymbolicType):
	def __init__(self, name, bitlen, z3_var=None, start=0, end=0):
		SymbolicType.__init__(self, name)
		self.concrete_value = 0L
		self.z3_start = start
		self.z3_end = end
		if z3_var != None:
			self.z3_var = z3_var
		else:
			self.z3_var = wrap.newIntegerVariable(self.name, bitlen)
		self._bitlen = bitlen

	def getBitLength(self):
		return self._bitlen

	def __repr__(self):
		return self.name + "#" + str(self.concrete_value)

	def isTerm(self):
		return True

	def symbolicEq(self, other):
		return self is other

	def getSymVariable(self):
		if self.z3_start == self.z3_end == 0:
			return [(self.name, self, self.z3_var)]
		else:
			return [(self.name, self, z3.extract(self.z3_var, self.z3_start, self.z3_end))]
