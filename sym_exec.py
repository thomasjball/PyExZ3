# Copyright: see copyright.txt

import os
import sys
import platform
import shutil
import logging
from optparse import OptionParser
from stats import getStats

from symbolic.loader import *
from symbolic.concolic import ConcolicEngine

print("PyExZ3 (Python Symbolic Execution via Z3)")

sys.path = [os.path.abspath(os.path.join(os.path.dirname(__file__)))] + sys.path
usage = "usage: %prog [options] <se_descr.py path>"
parser = OptionParser(usage=usage)
parser.add_option("-d", "--debug", dest="debug", action="store_true", help="Disassemble only")
parser.add_option("-l", "--log", dest="logfile", action="store", help="Save log output to a file", default="logfile")
parser.add_option("-f", "--force", dest="force_normalize", action="store_true", help="Force the regeneration of normalized files")
parser.add_option("-g", "--graph", dest="dot_graph", action="store_true", help="Generate a DOT graph of execution tree")
parser.add_option("-q", "--quiet", dest="quiet", action="store_true", help="Do not print statistics at the end of execution")
parser.add_option("-s", "--single-step", dest="single_step", action="store", help="Run only one iteration and save the pickled inputs in the specified file")

(options, args) = parser.parse_args()

if len(args) == 0 or not os.path.exists(args[0]):
	parser.error("Missing app to execute")
	sys.exit(1)
	
filename = os.path.abspath(args[0])
app_args = args[1:]
options.filename = filename

# Get the object describing the application
app = loaderFactory(filename)
if app == None:
	sys.exit(1)

logging.basicConfig(filename=options.logfile,level=logging.DEBUG)
log = logging.getLogger()
stats = getStats()
stats.pushProfile("se total")

print ("Running PyExZ3 on " + app.test_name)

stats.pushProfile("engine only")
engine = ConcolicEngine(app.create_invocation(),app.reset_callback,options)
if options.single_step:
	return_vals = engine.run(1)
	inputs = engine.generateAllInputs()
else:
	return_vals = engine.run()
stats.popProfile()

# print statistics
stats.popProfile() # SE total
if not options.quiet:
	print("---- Execution summary ----")
	log.info("\n" + stats.getProfilingOutput())
	log.info("\n" + stats.getCounterOutput())
	if options.logfile != "stdout":
		print(stats.getProfilingOutput())
		print(stats.getCounterOutput())

# check the result
result = app.execution_complete(return_vals)
	
if result == None or result == True:
	sys.exit(0);
else:
	sys.exit(1);	
