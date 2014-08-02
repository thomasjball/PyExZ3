import os
import sys

def filesys(x):
	# if file doesn't exist, create it and 
	g = 1
	if (os.path.exists("global.tmp")):
		file = open("global.tmp","r")
		g = int(file.readline())
		g = g + 3
		file.close()

	file = open("global.tmp","w")
	file.write(str(g))
	file.close()

	if (x == g):
		return 0
	elif (x == g+1):
		return 1	
	else:
		return 2		
