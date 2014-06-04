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

# Everything in this file is based on the documentation of the dis module
# that contains the explanation for each Python Opcode.
# This is for Python 2.6/2.7

import copy
import types
from symbolic_types import SymbolicType
import utils
import logging
from functools import reduce

def flatten(l):
	return reduce(lambda x,y : x + y, l)

log = logging.getLogger("se.opcodes")

class GenericOpCode:
	def __init__(self, opcode_id):
		self.name = "generic_no_name"
		# TBALL: this is a huge hack to represent storing into locations, thus the comment
                # "Be careful with this field, it becomes outdated (e.g. after assignements)"
		# TBALL: we should properly have a symbolic store
		self.reference = None 
		self.opcode_id = opcode_id

	def __repr__(self):
		return self.name

	def isSymbolic(self):
		if self.reference != None:
			return isinstance(self.reference, SymbolicType)
		else:
			return False

	def __eq__(self, other):
		if isinstance(other, GenericOpCode):
			return self.opcode_id == other.opcode_id
		else:
			return False

	# the reason for refreshing is that the context may change out
	# from underneath us when underlying code executes this operation
	# again
	def refreshRef(self, context):
		pass

	def getBitLength(self):
		utils.crash("getBitLength not implemented for this class")

	def shouldSaveValue(self):
		"""This method should not be overridden"""
		uninteresting_types = [
				types.FunctionType,
				types.ClassType,
				types.CodeType,
				types.InstanceType,
				types.LambdaType,
				types.GeneratorType,
				types.MethodType,
				types.UnboundMethodType,
				types.BuiltinFunctionType,
				types.BuiltinMethodType,
				types.ModuleType,
				types.FileType,
				types.FrameType,
				types.NoneType,
				#StpType,
				type(dict.__init__), # the wrapper-descriptor type
				]
		for t in uninteresting_types:
			if isinstance(self.reference, t):
				return False
		return True

class LocalReference(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = opcode[2]
		self.reference = context.getLocalVariable(self.name)
		if not self.isSymbolic() and self.shouldSaveValue():
			self.value = copy.copy(self.reference)

	def refreshRef(self, context):
		if self.reference == None:
			self.reference = context.getLocalVariable(self.name)
			if not self.isSymbolic() and self.shouldSaveValue():
				self.value = copy.copy(self.reference)

	def __repr__(self):
		return "LocalRef(" + self.name + ")"

	def getSymbolicVariables(self):
		if self.isSymbolic():
			return [self.reference]
		else:
			return []

	def getBitLength(self):
		if self.isSymbolic():
			return self.reference.getBitLength()
		else:
			return 0

class GlobalReference(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = opcode[2]
		self.reference = context.getGlobalVariable(self.name)
		if not self.isSymbolic() and self.shouldSaveValue():
			self.value = copy.copy(self.reference)

	def refreshRef(self, context):
		if self.reference == None:
			self.reference = context.getGlobalVariable(self.name)
			if not self.isSymbolic() and self.shouldSaveValue():
				self.value = copy.copy(self.reference)

	def __repr__(self):
		return "GlobalRef(" + self.name + ")"

	def getSymbolicVariables(self):
		if self.isSymbolic():
			return [self.reference]
		else:
			return []

	def getBitLength(self):
		if self.isSymbolic():
			return self.reference.getBitLength()
		else:
			return 0

class Attribute(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = opcode[2]
		if not len(stack) > 0:
			utils.crash("Empty stack while parsing an attribute")
		self.prev = stack.pop()
		if hasattr(self.prev.reference, self.name):
			self.reference = getattr(self.prev.reference, self.name)
			if not self.isSymbolic() and self.shouldSaveValue():
				try:
					self.value = copy.copy(self.reference)
				except TypeError:
					utils.crash("exception while copying this object: %s of type %s" % (self.reference, type(self.reference)))
		else:
			self.reference = None

	def __repr__(self):
		return repr(self.prev) + ".Attr(" + self.name + ")"

	def isSymbolic(self):
		if not GenericOpCode.isSymbolic(self):
			return self.prev.isSymbolic()
		else:
			return True

	def refreshRef(self, context):
		self.prev.refreshRef(context)
		if self.reference == None:
			self.reference = getattr(self.prev.reference, self.name)
			if not self.isSymbolic() and self.shouldSaveValue():
				self.value = copy.copy(self.reference)

	def getSymbolicVariables(self):
		if self.isSymbolic():
			l = [self.reference]
		else:
			l = []
		return l + self.prev.getSymbolicVariables()

	def getBitLength(self):
		if self.isSymbolic():
			return self.reference.getBitLength()
		else:
			return 0

class ConditionalJump(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = opcode[1]
		self.target = opcode[2]

		if not len(stack) > 0:
			utils.crash("Empty stack while parsing a conditional jump")
		self.condition = stack.pop()

	def __repr__(self):
		return self.name + "(" + repr(self.condition) + ") to " + repr(self.target)

	def isSymbolic(self): # If returns True this is a Constraint !!
		return self.condition.isSymbolic()

	def refreshRef(self, context):
		self.condition.refreshRef(context)

	def getSymbolicVariables(self):
		return self.condition.getSymbolicVariables()

	def getBitLength(self):
		return self.condition.getBitLength()

class Jump(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = opcode[1]
		self.target = opcode[2]

	def __repr__(self):
		return self.name + " to " + repr(self.target)

	def getSymbolicVariables(self):
		return []

class FunctionCall(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.params = []
		n_pos_params = opcode[2][0]
		n_kw_params = opcode[2][1]
		if len(stack) < n_pos_params + n_kw_params*2:
			utils.crash("Not enough elements on the stack for a function call. Required %d, available %d" % (n_pos_params + n_kw_params*2, len(stack)))
		for _p in range(n_kw_params):
			self.params.append(stack.pop())
			stack.pop() # ignore the key
		for _p in range(n_pos_params):
			self.params.append(stack.pop())
		self.params.reverse()
		self.fun_name = stack.pop()
		self.name = self.fun_name.name
		self.reference = self.fun_name.reference

	def __repr__(self):
		s = self.name + "("
		for p in self.params:
			s += repr(p) + ", "
		if len(self.params) > 0:
			s = s[:-2] + ")"
		else:
			s += ")"
		return s

	def isSymbolic(self):
		ret = self.fun_name.isSymbolic()
		for p in self.params:
			ret |= p.isSymbolic()
		return ret

	def refreshRef(self, context):
		for p in self.params:
			p.refreshRef(context)
		self.fun_name.refreshRef(context)
		self.reference = self.fun_name.reference

	def getSymbolicVariables(self):
		return flatten([p.getSymbolicVariables() for p in self.params])

	def getBitLength(self):
		return self.params[0].getBitLength()

class ConstantValue(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = "Constant"
		if opcode[1] == "BUILD_MAP":
			self.reference = {} # ATTN: This is not a reference to the dict created by the interpreter
		elif opcode[1] == "LOAD_CONST":
			self.reference = opcode[2]
		else:
			utils.crash("Unknown constant type: %s" % opcode[1])
		self.bitlen = 0

	def __repr__(self):
		return repr(self.reference)

	def getSymbolicVariables(self):
		return []

	def getBitLength(self):
		return self.bitlen

class UnaryOperator(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		if opcode[1] == "UNARY_NOT":
			self.name = "not"
		else:
			utils.crash("Unknown binary operator: %s" % str(opcode))

		self.expr = stack.pop()

	def __repr__(self):
		return self.name + " " + repr(self.expr)

	def isSymbolic(self):
		return self.expr.isSymbolic()

	def refreshRef(self, context):
		self.expr.refreshRef(context)

	def getSymbolicVariables(self):
		return self.expr.getSymbolicVariables()

	def getBitLength(self):
		return self.expr.getBitLength()

class BinaryOperator(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		if opcode[1] == "BINARY_MODULO":
			self.name = "%"
		elif opcode[1] == "COMPARE_OP":
			self.name = opcode[2]
		elif opcode[1] == "BINARY_AND":
			self.name = "&"
		elif opcode[1] == "BINARY_ADD":
			self.name = "+"
		elif opcode[1] == "BINARY_SUBTRACT":
			self.name = "-"
		elif opcode[1] == "BINARY_LSHIFT":
			self.name = "<<"
		elif opcode[1] == "BINARY_RSHIFT":
			self.name = ">>"
		elif opcode[1] == "BINARY_OR":
			self.name = "|"
		elif opcode[1] == "BINARY_XOR":
			self.name = "^"
		elif opcode[1] == "BINARY_MULTIPLY":
			self.name = "*"
		else:
			utils.crash("Unknown binary operator: %s" % str(opcode))
		self.right = stack.pop()
		self.left = stack.pop()

	def __repr__(self):
		return repr(self.left) + " " + self.name + " " + repr(self.right)

	def isSymbolic(self):
		return self.left.isSymbolic() or self.right.isSymbolic()

	def refreshRef(self, context):
		self.left.refreshRef(context)
		self.right.refreshRef(context)

	def getSymbolicVariables(self):
		return self.left.getSymbolicVariables() + self.right.getSymbolicVariables()

	def getBitLength(self):
		l = self.left.getBitLength()
		r = self.right.getBitLength()
		if l == 0:
			return r
		if r == 0:
			return l
		if r != l:
			raise NotImplementedError
		return l

class Assignment(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = "assignment"
		
		if opcode[1] == "STORE_SUBSCR":
			self.rvalue = Subscr(opcode, stack, context)
			self.lvalue = stack.pop()
		elif opcode[1] == "STORE_FAST":
			if context.getLocalVariable(opcode[2]) != None:
				self.rvalue = LocalReference(opcode, stack, context)
			elif context.getGlobalVariable(opcode[2]) != None:
				self.rvalue = GlobalReference(opcode, stack, context)
			else: # Separated to make it explicit, the variable has not been created yet
				self.rvalue = LocalReference(opcode, stack, context)
			self.lvalue = stack.pop()
		elif opcode[1] == "STORE_ATTR":
			self.lvalue = Attribute(opcode, stack, context)
			self.rvalue = stack.pop()
		else:
			utils.crash("Unknown assignment operator: %s" % str(opcode))

	def __repr__(self):
		return repr(self.rvalue) + " = " + repr(self.lvalue)

	def isSymbolic(self):
		return self.lvalue.isSymbolic() or self.rvalue.isSymbolic()

	def refreshRef(self, context):
		self.lvalue.refreshRef(context)
		self.rvalue.refreshRef(context)

	def getSymbolicVariables(self):
		return self.lvalue.getSymbolicVariables() + self.rvalue.getSymbolicVariables()

class Subscr(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = "subscr"
		self.needle = stack.pop()
		self.haystack = stack.pop()
		try:
			self.reference = self.haystack.reference[self.needle.reference]
			if not self.isSymbolic() and self.shouldSaveValue():
				self.value = copy.copy(self.reference)
		except KeyError:
			# Assignment to a new element, the reference does not exist yet
			self.reference = None
		self.bitlength = 0

	def __repr__(self):
		return repr(self.haystack) + "[" + repr(self.needle) + "]"

	def refreshRef(self, context):
		if self.reference == None:
			self.needle.refreshRef(context)
			self.haystack.refreshRef(context)
			self.reference = self.haystack.reference[self.needle.reference]
			if not self.isSymbolic() and not hasattr(self.reference, "__call__"):
				self.value = copy.copy(self.reference)

	def getSymbolicVariables(self):
		return self.needle.getSymbolicVariables() + self.haystack.getSymbolicVariables()

	def getBitLength(self):
		if self.isSymbolic():
			return self.reference.getBitLength()
		else:
			return self.bitlength

class ReturnValue(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = "return"
		self.value = stack.pop()

	def __repr__(self):
		return self.name + " " + repr(self.value)

	def isSymbolic(self):
		return self.value.isSymbolic()

	def refreshRef(self, context):
		self.value.refreshRef(context)

	def getSymbolicVariables(self):
		return self.value.getSymbolicVariables()

class BuildList(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		if opcode[1] == "BUILD_TUPLE":
			self.name = "tuple"
		elif opcode[1] == "BUILD_LIST":
			self.name = "list"
		else:
			utils.crash("Unknown BuildList opcode")
		self.elems = [ stack.pop() for _i in range(0, opcode[2]) ]

	def __repr__(self):
		return self.name + "(" + repr(self.elems) + ")"

	def isSymbolic(self):
		for e in self.elems:
			if e.isSymbolic():
				return True
		return False

	def refreshRef(self, context):
		for e in self.elems:
			e.refreshRef(context)

	def getSymbolicVariables(self):
		return flatten([ e.getSymbolicVariables() for e in self.elems ])

class PrintItem(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = "print_item"
		# Note: there is nothing about stack manipulation of PRINT_ITEM in documentation
		# but in practice it pops out the item
		self.value = stack.pop()

	def __repr__(self):
		return self.name + " " + repr(self.value)

	def isSymbolic(self):
		return False #nothing interesting in print

	def getSymbolicVariables(self):
		return []

class SetupLoop(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = "loop setup"

	def __repr__(self):
		return self.name

	def isSymbolic(self):
		return False

	def getSymbolicVariables(self):
		return []

class GetIterator(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = "iter"
		self.value = stack.pop()

	def __repr__(self):
		return self.name + "(" + repr(self.value) + ")"

	def isSymbolic(self):
		return self.value.isSymbolic()

	def getSymbolicVariables(self):
		return self.value.getSymbolicVariables()

class ForLoop(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = "for_loop"
		self.iterator = stack.pop()

	def __repr__(self):
		return self.name + " on " + repr(self.iterator)

	def isSymbolic(self):
		return self.iterator.isSymbolic()

	def getSymbolicVariables(self):
		return self.iterator.getSymbolicVariables()

class BreakLoop(GenericOpCode):
	def __init__(self, opcode, stack, context):
		GenericOpCode.__init__(self, opcode[0])
		self.name = "break"

	def __repr__(self):
		return self.name

	def isSymbolic(self):
		return False

	def getSymbolicVariables(self):
		return []

