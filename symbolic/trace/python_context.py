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

import inspect
import linecache
import __builtin__

# here we step from "native" Python state (frame) to our view of Python state (PythonContext)
# PythonContext is a view on Python state

class PythonContext:
	"""This object contains the whole context associated to a particular line of code executed."""
	def __init__(self, frame):
		self.filename = inspect.getfile(frame)
		self.lineno = frame.f_lineno
		if frame.f_code.co_name == "<module>": # module level code
			self.name = inspect.getmodulename(self.filename)
		else:
			self.name = frame.f_code.co_name
		self.code = linecache.getline(self.filename, self.lineno).strip()
		self.local_variables = frame.f_locals
		self.global_variables = frame.f_globals
		self.frame = frame

	def __repr__(self):
		s = "PythonContext instance\n"
		s += "\tfilename: %s\n" % self.filename
		s += "\tname: %s\n" % self.name
		s += "\tcode: %s\n" % self.code
		s += "\tlineno: %s\n" % self.lineno
		if self.local_variables != None:
			s += "\tlocal variables: %s\n" % str(self.local_variables.keys())
		if self.global_variables != None:
			s += "\tglobal variables: %s\n" % str(self.global_variables.keys())
		return s

	def getGlobalVariable(self, name):
		if name in self.global_variables:
			return self.global_variables[name]
		elif name in __builtin__.__dict__:
			return __builtin__.__dict__[name]
		else:
			return None

	def getLocalVariable(self, name):
		if name in self.local_variables:
			return self.local_variables[name]
		else:
			return None

