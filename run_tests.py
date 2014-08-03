import os
import re
import sys
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

parser = OptionParser()
(options, args) = parser.parse_args()

if len(args) == 0 or not os.path.exists(args[0]):
    parser.error("Please supply directory of tests")
    sys.exit(1)
    
test_dir = os.path.abspath(args[0])

if not os.path.isdir(test_dir):
    print("Please provide a directory of test scripts.")
    sys.exit(1)

files = [ f for f in os.listdir(test_dir) if re.search(".py$",f) ]

for f in files:
	# execute the python runner for this test
        full = test_dir + os.sep + f
        ret = os.system(sys.executable + " sym_exec.py -l "+full+".log "+full+" > "+full+".out")

        if (ret == 0):
            myprint(bcolors.SUCCESS, "✓", "Test " + f + " passed.")
        else:
            myprint(bcolors.FAIL, "✗", "Test " + f + " failed.")
