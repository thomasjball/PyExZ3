import os
import re
import sys
import subprocess
from optparse import OptionParser
from sys import platform as _platform

class bcolors:
    SUCCESS = '\033[32m'
    WARNING = '\033[33m'
    FAIL = '\033[31m'
    ENDC = '\033[0m'

def myprint(color, s, *args):
  if _platform != "win32" and sys.stdout.isatty():
    print(color, s, bcolors.ENDC, *args)
  else:
    print(*args)

usage = "usage: %prog [options] <test directory>"
parser = OptionParser()
parser.add_option("--cvc", dest="cvc", action="store_true", help="Use the CVC SMT solver instead of Z3", default=False)
parser.add_option("--z3", dest="cvc", action="store_false", help="Use the Z3 SMT solver")
(options, args) = parser.parse_args()

if len(args) == 0 or not os.path.exists(args[0]):
    parser.error("Please supply directory of tests")
    sys.exit(1)
    
test_dir = os.path.abspath(args[0])

if not os.path.isdir(test_dir):
    print("Please provide a directory of test scripts.")
    sys.exit(1)

files = [ f for f in os.listdir(test_dir) if re.search(".py$",f) ]

failed = []
for f in files:
	# execute the python runner for this test
        full = os.path.join(test_dir, f)
        with open(os.devnull, 'w') as devnull:
            solver = "--cvc" if options.cvc else "--z3"
            ret = subprocess.call([sys.executable, "pyexz3.py", "--m=25", solver, full], stdout=devnull)
        if (ret == 0):
            myprint(bcolors.SUCCESS, "✓", "Test " + f + " passed.")
        else:
            failed.append(f)
            myprint(bcolors.FAIL, "✗", "Test " + f + " failed.")

if failed != []:
	print("RUN FAILED")
	print(failed)
	sys.exit(1)
else:
	sys.exit(0)