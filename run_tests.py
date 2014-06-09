import os
import re
import sys
from optparse import OptionParser

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
	ret = os.system("python sym_exec.py -l "+full+".log "+full+" > "+full+".out")
	if (ret == 0):
		print("Test " + f + " passed.")
	else:
		print("Test " + f + " failed.")

