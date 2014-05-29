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

import ast
import logging
import utils
from symbolic_types.symbolic_type import SymbolicType
from z3 import *

_z3 = Solver()
log = logging.getLogger("se.z3")

z3_types = {}
z3_vars = {}

def int2BitVec(v, length):
	return BitVecVal(v, length)

def newIntegerVariable(name, bitlen):
	if name not in z3_vars:
		z3_vars[name] = BitVec(name,bitlen)
	else:
		log.error("Trying to create a duplicate variable")
	return z3_vars[name]

def findCounterexample(z3_asserts, z3_query, z3_variables):
	"""Tries to find a counterexample to the query while
	   asserts remains valid."""
	_z3.push()
	_z3.assert_exprs(z3_asserts)
	_z3.assert_exprs(Not(z3_query))
#	print _z3.assertions()
	ret = _z3.check()
	if ret == unsat:
		log.warning("Z3: UNSAT")
		print _z3.unsat_core()
		_z3.pop()
		return None
	elif ret == unknown:
		log.error("Z3: UNKNOWN")
		_z3.pop()
		return None
	res = []
        model = _z3.model()
#	print "Model is "
#	print model
	for var_name in z3_variables:
		(instance, z3_var) = z3_variables[var_name]
		ce = model.eval(z3_var)
		res.append((var_name, instance, ce.as_signed_long()))
	_z3.pop()
	return res

def notExpr(expr):
	return Not(expr)

def extract(var, start, end):
	return Extract(start, end, var)

def eqExpr(e1, e2):
	return e1 == e1

def ast2SymExpr(expr, bitlen):
	if isinstance(expr, ast.BinOp):
		z3_l = ast2SymExpr(expr.left, bitlen)
		z3_r = ast2SymExpr(expr.right, bitlen)
		if isinstance(expr.op, ast.Add):
			return z3_l + z3_r
		if isinstance(expr.op, ast.Sub):
			return z3_l - z3_r
		elif isinstance(expr.op, ast.Mult):
			return z3_l * z3_r
		# TBALL: more conversions to do here
		else:
			utils.crash("Unknown BinOp during conversion from ast to Z3 (expressions): %s" % expr.op)
	elif isinstance(expr, SymbolicType):
		return expr.getSymVariable()[0][2]
	elif isinstance(expr, int) or isinstance(expr, long):
		return int2BitVec(expr, bitlen)
	else:
		utils.crash("Unknown node during conversion from ast to stp (expressions): %s" % expr)

