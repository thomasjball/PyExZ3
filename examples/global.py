import sys

g = 1

def global(x):
	# if file doesn't exist, create it and 
	if (os.path.exists("global.tmp")):
		file = open("global.tmp","r")
		g = int(file.readline())
		g = g + 1
		file.close()

	file = open("global.tmp","w")
	file.write(str(g))
	file.close()

	if (x == g):
		return 0
	else:
		return 1			