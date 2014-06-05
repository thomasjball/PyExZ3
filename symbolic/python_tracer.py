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

import sys
import threading
import dis
import os
import pprint

# Prime number generator, used to create new opcode IDs. Each module is associated with its own prime number.
from eratosthenes import eratosthenes 
from python_context import PythonContext
from bytecode_parser import ByteCodeParser
import utils
import logging
from stats import getStats

log = logging.getLogger("se.tracer")
stats = getStats()

class Ignore:
	""" Copied from trace.py, in the Python sources. """
 	def __init__(self, modules = None, dirs = None):
		self._mods = modules or []
		self._dirs = dirs or []
		self._dirs = map(os.path.normpath, self._dirs)
		self._ignore = { '<string>': 1 }
 	
	def modname(self, path):
		"""Return a plausible module name for the path."""
		base = os.path.basename(path)
		filename = os.path.splitext(base)[0]
		return filename

 	def names(self, filename):
		modulename = self.modname(filename)
 		if modulename in self._ignore:
 			return self._ignore[modulename]
 	
		# haven't seen this one before, so see if the module name is
		# on the ignore list. Need to take some care since ignoring
		# "cmp" musn't mean ignoring "cmpcache" but ignoring
		# "Spam" must also mean ignoring "Spam.Eggs".
		for mod in self._mods:
			if mod == modulename: # Identical names, so ignore
				self._ignore[modulename] = 1
				return 1
			# check if the module is a proper submodule of something on
			# the ignore list
			n = len(mod)
			# (will not overflow since if the first n characters are the
			# same and the name has not already occurred, then the size
			# of "name" is greater than that of "mod")
			if mod == modulename[:n] and modulename[n] == '.':
				self._ignore[modulename] = 1
				return 1
		
		# Now check that __file__ isn't in one of the directories
		if filename is None:
			# must be a built-in, so we must ignore
			self._ignore[modulename] = 1
			return 1
		
		# Ignore a file when it contains one of the ignorable paths
		for d in self._dirs:
			if filename.startswith(d + os.sep):
				self._ignore[modulename] = 1
				return 1
		
		# Tried the different ways, so we don't ignore this module
		self._ignore[modulename] = 0
		return 0

class PythonTracer:
	def __init__(self, debug):
		# this line is very important; if the ignore directories are not correctly set 
		# (especially PYTHONHOME), the whole thing silently fails to work. Should make
		# more robust in future
		self.ignore = Ignore(modules = [], dirs = [os.path.dirname(__file__), os.environ["PYTHONHOME"]])

		self.SI = None
		self.trace_func = self._Tracer
		self.no_symbolic = debug

		self.unique_op_map = {}
		self.execution_context = None
		self.known_code_blocks = {}

		self.parser = ByteCodeParser(self)
		self.prime_generator = eratosthenes()
		self.arguments = {}
		self.inside_tracing_code = True
		self.function_to_be_traced = None

	def setInterpreter(self, i):
		self.SI = i

	def setFunction(self, func):
		log.debug("Preparing to trace the function: %s" % func.__name__)
		self.function_to_be_traced = func

	def addFunParam(self, name, value):
		self.arguments[name] = value

	def clearFunParams(self):
		self.arguments = {}

	def execute(self):
		log.debug("Executing with arguments: %s" % self.arguments)
		if self.function_to_be_traced != None:
			return self._symbolicExecFunction()
		else:
			utils.crash("Nothing to trace!")

	def _Tracer(self, frame, event, arg):
		self.inside_tracing_code = True
		ctx = PythonContext(frame)
		self.execution_context = ctx
		if event == "line" and not self.no_symbolic:
			key = self.execution_context.filename + ":" + self.execution_context.name
			if not key in self.known_code_blocks:
				utils.crash("Executing something in an unknown code block")

			(codeblock, op_ids, linestarts) = self.known_code_blocks[key]
			pc = self._getOpID(frame.f_lasti)
			if not pc in op_ids:
				utils.crash("Known codeblock, unknown instruction")
			if not len(linestarts) >= 1:
				utils.crash("Known codeblock, no linestarts")

			# This code looks for the first and last opcodes in the current code line
			# in theory lasti is always on a line start, but in practice that is not true
			# for loop conditions, so we just assume lasti to be anywhere in a line
			if len(linestarts) == 1:
				stmts = self.parser.parse(codeblock)
			else:
				start = None
				end = None
				aux = linestarts.values()
				aux.sort()
				if pc >= aux[-1]:
					start = aux[-1]
				else:
					for i in range(0, len(aux)):
						if aux[i] <= pc and pc < aux[i+1]:
							start = aux[i]
							end = aux[i+1]
							break
				for cb in codeblock:
					if cb[0] == start:
						start = codeblock.index(cb)
						break
				if end == None:
					end = 0
				else:
					for cb in codeblock:
						if cb[0] == end:
							end = codeblock.index(cb)
							break
				# The codeblock is upside-down...
				aux = start
				start = end + 1
				end = aux + 1
				stats.pushProfile("bytecode parsing")
				stmts = self.parser.parse(codeblock[start:end])
				stats.popProfile()

			for s in stmts:
				if self.SI.isGoodConditional(s):
					stats.pushProfile("path to constraint")
					self.SI.recordConditional(s)
					stats.popProfile()

		elif event == "call": # Use the same filtering mechanism as in Python's trace module

			if ctx.filename and self.ignore.names(ctx.filename):
				self.inside_tracing_code = False
				return None

			key = self.execution_context.filename + ":" + self.execution_context.name

			if key not in self.known_code_blocks:
				stats.pushProfile("disassembly")
				(codeblock, op_ids) = self._disassemble(frame.f_code, frame.f_lasti)
				stats.popProfile()
				linestarts = dict(dis.findlinestarts(frame.f_code))
				aux = {}
				for l in linestarts:
					aux[linestarts[l]] = self._getOpID(l)
				self.known_code_blocks[key] = (codeblock, op_ids, aux)

			if self.no_symbolic:
				(codeblock, op_ids, linestarts) = self.known_code_blocks[key]
				pprint.pprint(ctx)
				pprint.pprint(codeblock)
				pprint.pprint(linestarts)
				print "--------"
		else:
			# DANGER: we lose visibility into error source here
			# TODO: this branch can be executed when
			# TODO: our code throws an exception when invoked
			# TODO: should we stop everything?
			# TODO: event == "exception"
			pass

		self.inside_tracing_code = False
		return self.trace_func

	def _getOpID(self, cb_id):
		""" returns tuple (context_id, op_id)"""
		cb_id = cb_id + 1 # No 0
		if not cb_id != 0:
			utils.crash("cb_id must be different that zero")

		key = self.execution_context.filename + ":" + self.execution_context.name
		if key in self.unique_op_map.keys():
			return (self.unique_op_map[key], cb_id)
		else:
			self.unique_op_map[key] = self.prime_generator.next()
			return (self.unique_op_map[key], cb_id)

	def _symbolicExecFunction(self):
		threading.settrace(self.trace_func)
		sys.settrace(self.trace_func)
		try:
			self.inside_tracing_code = False
			result = self.function_to_be_traced(**self.arguments)
		finally:
			self.inside_tracing_code = True
			sys.settrace(None)
			threading.settrace(None)
		return result

	def _disassemble(self, co, lasti):
		"""Disassemble only the lasti instruction line of the code object co. No longer true."""
		code = co.co_code
#		linestarts = dict(dis.findlinestarts(co))
		n = len(code)
#		i = lasti
		i = 0
		extended_arg = 0
		free = None
#		try:
#			in_line = linestarts[i]
#		except KeyError:
#			return None

		code_dis = []
		op_ids = set()

		while i < n:
			c = code[i]
			op = ord(c)
#			if i in linestarts:
#				if linestarts[i] != in_line:
#					break

			pos = i
			name = dis.opname[op]

			i = i + 1
			if op >= dis.HAVE_ARGUMENT:
				oparg = ord(code[i]) + ord(code[i+1])*256 + extended_arg
				arg = (ord(code[i]), ord(code[i+1])) # if name == "CALL_FUNCTION": (n. positional params, n. kw params)
				extended_arg = 0
				i = i+2
				if op == dis.EXTENDED_ARG:
					extended_arg = oparg*65536L

				if op in dis.hasconst:
					arg = co.co_consts[oparg]
				elif op in dis.hasname:
					arg = co.co_names[oparg]
				elif op in dis.hasjabs:
					arg = self._getOpID(oparg)
				elif op in dis.hasjrel:
					arg = self._getOpID(i + oparg)
				elif op in dis.haslocal:
					arg = co.co_varnames[oparg]
				elif op in dis.hascompare:
					arg = dis.cmp_op[oparg]
				elif op in dis.hasfree:
					if free is None:
						free = co.co_cellvars + co.co_freevars
					arg = free[oparg]
				elif name in ["BUILD_TUPLE", "BUILD_LIST"]:
					arg = oparg
			else:
				arg = None
			code_dis.append((self._getOpID(pos), name, arg))
			op_ids.add(self._getOpID(pos))

		code_dis.reverse() # make it a real stack, LIFO ordering
		return (code_dis, op_ids)

