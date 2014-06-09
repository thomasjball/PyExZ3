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

import os
import sys
import shutil
import cPickle
import logging
from symbolic.loader import loaderFactory
from optparse import OptionParser
from stats import getStats
from symbolic.loader import Loader
from symbolic.concolic import ConcolicEngine
from symbolic import preprocess

print "PyExZ3 (Python Symbolic Execution via Z3)"

if not "PYTHONHOME" in os.environ:
	print "Please set PYTHONHOME to the location of your python installation."
	sys.exit(1)

sys.path = [os.path.abspath(os.path.join(os.path.dirname(__file__)))] + sys.path
usage = "usage: %prog [options] <se_descr.py path>"
parser = OptionParser(usage=usage)
parser.add_option("-d", "--debug", dest="debug", action="store_true", help="Disassemble only")
parser.add_option("-l", "--log", dest="logfile", action="store", help="Save log output to a file", default="logfile")
parser.add_option("-f", "--force", dest="force_normalize", action="store_true", help="Force the regeneration of normalized files")
parser.add_option("-q", "--quiet", dest="quiet", action="store_true", help="Do not print statistics at the end of execution")
parser.add_option("-s", "--single-step", dest="single_step", action="store", help="Run only one iteration and save the pickled inputs in the specified file")

(options, args) = parser.parse_args()

if len(args) == 0 or not os.path.exists(args[0]):
	parser.error("Missing app to execute")
	sys.exit(1)
	
filename = os.path.abspath(args[0])
app_args = args[1:]

# Get the object describing the application
app = loaderFactory(filename)
if app == None:
	sys.exit(1)

logging.basicConfig(filename=options.logfile,level=logging.DEBUG)
log = logging.getLogger()
stats = getStats()
stats.pushProfile("se total")

se_instr_dir = os.path.abspath("se_normalized")
if options.force_normalize and os.path.exists(se_instr_dir):
	shutil.rmtree(se_instr_dir)
if not os.path.exists(se_instr_dir):
	os.mkdir(se_instr_dir)

print "Running PyExZ3 on " + app.test_name

os.chdir(se_instr_dir)

# instrument the code to be analyzed
preprocess.instrumentModule(app.test_name + ".py", se_instr_dir, is_app=True, in_dir=os.path.dirname(filename))

sys.path = [ se_instr_dir ] + sys.path

stats.pushProfile("engine only")
engine = ConcolicEngine(app.create_invocation(),app.reset_callback,options.debug)
if options.single_step:
	return_vals = engine.run(1)
	inputs = engine.generateAllInputs()
	cPickle.dump(inputs, file(options.single_step, "w"), -1)
else:
	return_vals = engine.run()
stats.popProfile()

# print statistics
stats.popProfile() # SE total
if not options.quiet:
	print "---- Execution summary ----"
	log.info("\n" + stats.getProfilingOutput())
	log.info("\n" + stats.getCounterOutput())
	if options.logfile != "stdout":
		print stats.getProfilingOutput()
		print stats.getCounterOutput()

# check the result
result = app.execution_complete(return_vals)
if result == None or result == True:
	sys.exit(0);
else:
	sys.exit(1);	

