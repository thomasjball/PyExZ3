(options, args) = parser.parse_args()

if len(args) == 0 or not os.path.exists(args[0]):
	parser.error("Missing app to execute")
	sys.exit(1)
	
app_dir = os.path.abspath(args[0])
app_args = args[1:]

if not os.path.isdir(app_dir):
	print "Please provide a directory name for app."
	sys.exit(1)

files = [ f[:-3] for f in os.listdir(test_dir) if re.search(".py$",f) ]

for t in files:
	# execute the python runner for this test
