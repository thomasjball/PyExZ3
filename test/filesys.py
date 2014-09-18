import os
import sys

def filesys(x):
	# if file doesn't exist, create it and 
	g = 1
	if (os.path.exists("tmp.txt")):
		file = open("tmp.txt","r")
		g = int(file.readline())
		g = g + 3
		file.close()

	file = open("tmp.txt","w")
	file.write(str(g))
	file.close()

	if (x == g):
		return 0
	elif (x == g+1):
		return 1	
	else:
		return 2		

def expected_result_set():
	return [2]
