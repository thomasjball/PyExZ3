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
import traceback
#import logging
#log = logging.getLogger("se.utils")

def _traceback():
	stack = traceback.format_stack()
	return stack[:-2]

def crash(msg):
	stack = _traceback()
#	log.critical("\n"+"".join(stack))
#	log.critical(msg)
	sys.exit(-1)

def serialize_dict(d):
	nd = {}
	keys = d.keys()
	keys.sort()
	for k in keys:
		if isinstance(d[k], dict):
			nd[k] = serialize_dict(d[k])
		elif hasattr(d[k], "__getstate__"):
			nd[k] = d[k].__getstate__()
		else:
			nd[k] = d[k]
	return nd

def flatten_dict(d):
	keys = d.keys()
	keys.sort()
	flat_attrs = map(lambda x: (x, d[x]), keys)
	return [item for subtuple in flat_attrs for item in subtuple] # Flatten the list of tuples

def serialize_list_of_dicts(l):
	nl = []
	for d in l:
		nd = serialize_dict(d)
		nl.append(nd)
	nl.sort(key=flatten_dict)
	return nl

