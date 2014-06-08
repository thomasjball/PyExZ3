# test_dir = os.path.abspath(os.path.dirname(__file__))

(options, args) = parser.parse_args()

if len(args) == 0 or not os.path.exists(args[0]):
	parser.error("Missing app to execute")
	sys.exit(1)
	
app_dir = os.path.abspath(args[0])
app_args = args[1:]

if not os.path.isdir(app_dir):
	print "Please provide a directory name for app."
	sys.exit(1)

# add the app directory to the import path, just to get the configuration
sys.path = [app_dir] + sys.path

app_description = __import__("test_descr")

for t in test_descr.TESTS:
	# execute the python runner for this test
	