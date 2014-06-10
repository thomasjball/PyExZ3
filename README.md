PyExZ3
======

###NICE Symbolic Execution for Python (Z3)

This code is a port of the NICE project's (http://code.google.com/p/nice-of/) 
symbolic execution engine for Python to use the Z3 theorem prover (http://z3.codeplex.com).
The port removes all the NICE-specific dependences, platform-specific code, and
makes various improvements so the code base can be used by students or anyone wanting to
experiment with dynamic symbolic execution.

###Setup instructions:

- Make sure that you use Python 32-bit (64-bit) if-and-only-if you use the Z3 32-bit (64-bit) binaries. Testing so far has been for 32-bit binaries only. 
- Install Python version 2.7.6 (https://www.python.org/download/releases/2.7.6/)
- Install Z3 to directory Z3HOME from http://z3.codeplex.com/releases (click on the "Planned" link on the right to get the latest binaries for all platforms)
- Add Z3HOME\bin to PATH and PYTHONPATH
- MacOS: see setup.sh for Homebrew default locations for Python and Z3

### MacOS specific

1. Grab yourself a Brew at http://brew.sh/
2. Get the newest python or python3 version: `brew install python`
3. Have the system prefer brew python over system python: `echo export PATH='/usr/local/bin:$PATH' >> ~/.bash_profile`  - 
4. Get z3: `brew install homebrew/science/z3`
5. Clone this repository: `git clone https://github.com/thomasjball/PyExZ3.git` 
6. Set the PATH: `. PyExZ3/setup.sh`  (do not run the setup script in a subshell `./ PyExZ3/`)

### Check that everything works:
- "python run_tests.py test" should pass all tests
- "python sym_exec.py test\FILE.py" to run a single test from test directory
