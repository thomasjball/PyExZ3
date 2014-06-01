PyExZ3
======

NICE Symbolic Execution for Python (Z3)

This code is a port of the NICE project's (http://code.google.com/p/nice-of/) 
symbolic execution engine for Python to use the Z3 theorem prover (http://z3.codeplex.com).
The port removes all the NICE-specific dependences, platform-specific code, and
makes various improvements so the code base can be used by students or anyone wanting to
experiment with dynamic symbolic execution.

Setup instructions:

- Make sure that you use Python 32-bit (64-bit) if-and-only-if you use the Z3 32-bit (64-bit) binaries. Testing so far has been for 32-bit binaries only. 
- Install Python version 2.7.6 (https://www.python.org/download/releases/2.7.6/)
- Install Z3 to directory Z3HOME from http://z3.codeplex.com/releases (click on the "Planned" link on the right to get the latest binaries for all platforms)
- Set PYTHONHOME to the location of your Python distribution
- Add PYTHOHHOME to PATH
- Add Z3HOME\bin to PATH and PYTHONPATH
