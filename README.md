PyExZ3
======

NICE Symbolic Execution for Python (Z3)

This code is a port of the NICE project's (http://code.google.com/p/nice-of/) 
symbolic execution engine for Python to use the Z3 theorem prover (http://z3.codeplex.com).
The port removes all the NICE-specific dependences and forms the basis for
experimentation with symbolic execution on a small code base across
a variety of platforms.

Requirements:

- Python version 2.7.6 (https://www.python.org/download/releases/2.7.6/)
- Install Z3 to directory *Z3HOME* from http://z3.codeplex.com/releases (click on the "Planned" link on the right to get the latest binaries for all platforms)
- Make sure that you are using Python 32-bit (64-bit) then use the Z3 32-bit (64-bit) binaries.

Setup instructions:

- set PYTHONHOME to the location of your Python distribution
- add PYTHOHHOME to PATH
- add *Z3HOME*\bin to PATH and PYTHONPATH
