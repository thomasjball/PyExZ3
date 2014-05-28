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

import os
import sys
import shutil
import cPickle
import logging
from optparse import OptionParser
from stats import getStats
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
parser.add_option("-l", "--log", dest="logfile", action="store", help="Save log output to a file", default="stdout")
parser.add_option("-f", "--force", dest="force_normalize", action="store_true", help="Force the regeneration of normalized files")
parser.add_option("-q", "--quiet", dest="quiet", action="store_true", help="Do not print statistics at the end of execution")
parser.add_option("-s", "--single-step", dest="single_step", action="store", help="Run only one iteration and save the pickled inputs in the specified file")

(options, args) = parser.parse_args()

if len(args) == 0 or not os.path.exists(args[0]):
	parser.error("Missing app to execute")
	sys.exit(1)
	
app_dir = os.path.abspath(args[0])
# TBALL: can the following fail?
app_args = args[1:]

if not os.path.isdir(app_dir):
	print "Please provide a directory name for app."
	sys.exit(1)
app_dir = os.path.abspath(app_dir)

logging.basicConfig(filename=options.logfile,level=logging.DEBUG)
log = logging.getLogger()
stats = getStats()
stats.pushProfile("se total")

se_dir = os.path.abspath(os.path.dirname(__file__))
se_instr_dir = os.path.abspath("se_normalized")
if options.force_normalize and os.path.exists(se_instr_dir):
	shutil.rmtree(se_instr_dir)
if not os.path.exists(se_instr_dir):
	os.mkdir(se_instr_dir)

os.chdir(app_dir)

# add the app directory to the import path, just to get the configuration
sys.path = [app_dir] + sys.path

app_description = __import__("se_descr")

# then remove it and put in the instrumented version directory
sys.path[0] = se_instr_dir

# Get the object describing the application
app_description = app_description.factory(app_args)

print "Running PyExZ3 on " + app_description.APP_NAME

preprocess.instrumentLibrary(os.path.join(se_dir, "sym_exec_lib"), se_instr_dir)

for m in app_description.NORMALIZE_MODS:
	preprocess.instrumentModule(m, se_instr_dir, is_app=True)

for p in app_description.NORMALIZE_PACKAGES:
	preprocess.instrumentPackage(p, se_instr_dir)

engine = ConcolicEngine(options.debug)

invocation_sequence = app_description.create_invocations()
engine.setInvocationSequence(invocation_sequence)

engine.setResetCallback(app_description.reset_callback)

stats.pushProfile("engine only")
if options.single_step:
	return_vals = engine.run(1)
	inputs = engine.generateAllInputs()
	cPickle.dump(inputs, file(options.single_step, "w"), -1)
else:
	return_vals = engine.run()
stats.popProfile()

app_description.execution_complete(return_vals)

stats.popProfile() # SE total

if not options.quiet:
	print "---- Execution summary ----"
	log.info("\n" + stats.getProfilingOutput())
	log.info("\n" + stats.getCounterOutput())
	if options.logfile != "stdout":
		print stats.getProfilingOutput()
		print stats.getCounterOutput()
