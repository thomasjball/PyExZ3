# Copyright: see copyright.txt

import os
import sys
import logging
from optparse import OptionParser

from symbolic.loader import *
from symbolic.concolic import ConcolicEngine

print("PyExZ3 (Python Symbolic Execution via Z3)")

sys.path = [os.path.abspath(os.path.join(os.path.dirname(__file__)))] + sys.path

usage = "usage: %prog [options] <path to a *.py file>"
parser = OptionParser(usage=usage)

parser.add_option("-l", "--log", dest="logfile", action="store", help="Save log output to a file", default="")
parser.add_option("-g", "--graph", dest="dot_graph", action="store_true", help="Generate a DOT graph of execution tree")
parser.add_option("-m", "--max-iters", dest="max_iters", type="int", help="Run specified number of iterations", default=0)

(options, args) = parser.parse_args()

if not (options.logfile == ""):
	logging.basicConfig(filename=options.logfile,level=logging.DEBUG)

if len(args) == 0 or not os.path.exists(args[0]):
	parser.error("Missing app to execute")
	sys.exit(1)

filename = os.path.abspath(args[0])
	
# Get the object describing the application
app = loaderFactory(filename)
if app == None:
	sys.exit(1)

print ("Running PyExZ3 on " + app.getName())

engine = ConcolicEngine(app.createInvocation())
returnVals,path = engine.run(options.max_iters)

# check the result
result = app.executionComplete(returnVals)

# output DOT graph
if (options.dot_graph):
	file = open(filename+".dot","w")
	file.write(path.toDot())	
	file.close()

if result == None or result == True:
	sys.exit(0);
else:
	sys.exit(1);	
