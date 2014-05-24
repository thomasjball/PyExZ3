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
- Z3 (Windows: http://z3.codeplex.com/releases, Other platforms, build from source: http://z3.codeplex.com/SourceControl/latest#README); install Z3 to directory *Z3HOME*
- If you are using Python 32-bits, then you must use the 32-bit Z3 binaries.

Setup instructions:

- add *Z3HOME*\bin to PATH and PYTHONPATH

