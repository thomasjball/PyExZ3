# Copyright: see copyright.txt

import sys
import traceback
import logging
log = logging.getLogger("se.utils")

def _traceback():
	stack = traceback.format_stack()
	return stack[:-2]

def crash(msg):
	stack = _traceback()
	print("\n"+"".join(stack))
	print(msg)
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

