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

import bytecode_opcodes as bc
import utils
import logging

log = logging.getLogger("se.parser")

# Overall note: We assume that each codeblock leaves the stack in the previous state,
# i.e. we do not reuse variables remaining on the stack from previous codeblock.
# This assumption may fail if Python starts to do fancy optimizations of bytecode

OPS = { "LOAD_FAST": bc.LocalReference,
		"LOAD_ATTR": bc.Attribute,
		"JUMP_IF_TRUE": bc.ConditionalJump,
		"JUMP_IF_FALSE": bc.ConditionalJump,
		# Note: We assume that conditional jump is the last statement in the block
		# and thus we do not need POP, see comment above POP_TOP
		"POP_JUMP_IF_TRUE": bc.ConditionalJump,
		"POP_JUMP_IF_FALSE": bc.ConditionalJump,
		"JUMP_IF_TRUE_OR_POP": bc.ConditionalJump,
		"JUMP_IF_FALSE_OR_POP": bc.ConditionalJump,
		"LOAD_GLOBAL": bc.GlobalReference,
		"CALL_FUNCTION": bc.FunctionCall,
		"CALL_FUNCTION_KW": bc.FunctionCall,
		"CALL_FUNCTION_VAR_KW": bc.FunctionCall,
		"LOAD_CONST": bc.ConstantValue,
		"BINARY_MODULO": bc.BinaryOperator,
		"BUILD_MAP": bc.ConstantValue,
		"STORE_SUBSCR": bc.Assignment,
		"STORE_ATTR": bc.Assignment,
		"STORE_MAP": bc.Assignment,
		"JUMP_FORWARD": bc.Jump,
		"COMPARE_OP": bc.BinaryOperator,
		"STORE_FAST": bc.Assignment,
		"BINARY_SUBSCR": bc.Subscr,
		"BINARY_AND": bc.BinaryOperator,
		"BINARY_ADD": bc.BinaryOperator,
		"BINARY_SUBTRACT": bc.BinaryOperator,
		"BINARY_LSHIFT": bc.BinaryOperator,
		"BINARY_OR": bc.BinaryOperator,
		"BINARY_MULTIPLY": bc.BinaryOperator,
		"UNARY_NOT": bc.UnaryOperator,
		"RETURN_VALUE": bc.ReturnValue,
		"BUILD_TUPLE": bc.BuildList,
		"BUILD_LIST": bc.BuildList,
		# Note: We are not interested in PRINT_ITEM operations, but we need their op_ids because
		# otherwise we cannot correctly catch the branch of following statements:
		# if expr:
		#   print "something"
		#   do_something;
		"PRINT_ITEM": bc.PrintItem,
		"SETUP_LOOP": bc.SetupLoop,
		"SETUP_EXCEPT": bc.SetupLoop,
		"GET_ITER": bc.GetIterator,
		"FOR_ITER": bc.ForLoop,
		"BREAK_LOOP": bc.BreakLoop,
		"END_FINALLY": bc.BreakLoop,
}

# Note: We assume that POP_TOP instruction is used only at the end of the block
# and it is used to clear the stack after the last statement.
# We do not want to do pop here -- in fact, the top of the stack is what is interesting for us
OPS_IGNORE = ["POP_TOP", "PRINT_NEWLINE", "JUMP_ABSOLUTE", "POP_BLOCK", "IMPORT_NAME", "IMPORT_STAR", "IMPORT_FROM", "STORE_NAME", "LOAD_NAME", "MAKE_FUNCTION"]

OPS_IGNORE_POP = []

class ByteCodeParser:
	def __init__(self, tracer):
		self.PT = tracer

	def parse(self, cb):
		""" components is stack, but at the end should contain a list of statements """
		components = []
#		log.debug("Parsing this codeblock: %s" % cb)
		if len(cb) == 0:
#			log.debug("Skipping empty codeblock")
			return components
		while len(cb) > 0:
			op = cb.pop()
			if op[1] in OPS_IGNORE:
				pass
			elif op[1] in OPS_IGNORE_POP:
				components.pop()
			elif op[1] in OPS:
				elem = OPS[op[1]](op, components, self.PT.execution_context)
				components.append(elem)
			else:
				utils.crash("Opcode %s is unknown: %s" % (op[1], cb))

		return components

