PyExZ3
======

###A Python Explorer using Z3

This code is a substantial rewrite of the NICE project's
(http://code.google.com/p/nice-of/) symbolic execution engine for
Python to use the Z3 theorem prover (http://z3.codeplex.com). We have
removed the NICE-specific dependences, platform-specific code, and
made various improvements, documented below, so it can be used
by anyone wanting to experiment with dynamic symbolic execution.

In the limit, **PyExZ3** tries to *explore/execute* all the paths in a
Python function by:
-  executing the function on a concrete input to trace a path through the control flow of the function;
- using symbolic execution along the path to determine how the conditions inside the
function depend on the function's parameters;
- generating new values for the parameters to drive the function to yet uncovered paths, using Z3.  

For small programs without loops or recursion, 
**PyExZ3** may be able to explore all feasible paths.

A novel aspect of the rewrite is to rely solely on Python's operator
overloading to accomplish all the interception needed for symbolic
execution; no AST rewriting or bytecode instrumentation is required,
as was done in the NICE project. This significantly improves the
robustness and portability of **PyExZ3**, as well as reducing its
size.

###Setup instructions:

- Make sure that you use Python 32-bit (64-bit) if-and-only-if you use the Z3 32-bit (64-bit) binaries. Testing so far has been on Python 3.2.3 and 32-bit.
- Install Python 3.2.3 (https://www.python.org/download/releases/3.2.3/)
- Install the latest "unstable" release of Z3 to directory Z3HOME from http://z3.codeplex.com/releases (click on the "Planned" link on the right to get the latest binaries for all platforms)
- Add Z3HOME\bin to PATH and PYTHONPATH
- MacOS: setup.sh for Homebrew default locations for Python and Z3; see end for MacOS specifi instructions
- Optional:
-- install GraphViz utilities (http://graphviz.org/)

### Check that everything works:

- `python run_tests.py test` should pass all tests

- `python pyexz3.py test\FILE.py` to run a single test from the test directory

### Usage of PyExZ3

- **Basic usage**: give a Python file `FILE.py` as input. By default, `pyexz3` expects `FILE.py` to contain a function named `FILE` where symbolic execution will start:

  - `pyexz3 FILE.py`

- **Starting function**: You can override the default starting function with `--start MAIN`, where `MAIN` is the name of a  function in `FILE`: 

  - pyexz3 `--start MAIN` FILE.py

- **Bounding the number of iterations** of the path exploration is essential when you are
analyzing functions with loops and/or recursion. Specify a bound using the `max-iters` flag:

  - pyexz3 `--max-iters 42` FILE.py

- **Arguments to starting function**: by default, pyexz3 associates a symbolic integer
(with initial value 0) for each parameter of the starting function. 
You can decorate the starting function to provde concrete values for parameters 
(`@concrete`) so that they never will be treated symbolically; you can also specify 
which values should be treated symbolically (`@symbolic`) - the type of the associated 
initial value for the argument will be used to determine the proper symbolic type 
(if one exists). Here is an example, where parameters `a` and `b` are treated concretely
and will have initial values `1` and `2`, and parameter `c` will be treated as a symbolic
integer input with the initial value `3`. Since parameter `d` is not
specified, it will be treated as a symbolic integer input with the initial value 0:

```
from symbolic.args import *

@concrete(a=1,b=2)
@symbolic(c=3)
startingfun(a,b,c,d):
    ...
```

- **Output**: `pyexz3` prints the list of generated inputs and observed return values
to standard out; the lists of generated inputs and the corresponding return values are
returned by the exploration engine to `pyexz3` where they can be used for other 
purposes, as described below.

- **Oracle test functions** are used for testing of the tool. If the `FILE.py` contains a function named `expected_result` then after path exploration is complete, the list of return values will be compared against the list returned by `expected_result`. More precisely, the two lists are converted into bags and the bags compared for equality.  If a function named
`expected_result_set` is present instead, the list are converted into sets and the sets are compared for equality. 
List equality is too strong a criteria for testing, since small changes to programs can lead to paths being explored
in different orders. 

- **Import behavior**: the location of the `FILE.py` is added to the import path so that all imports in `FILE.py` 
relative to that file will work.

- **Other options**
  - `--graph` DOTFILE
  - `--log` LOGFILE

### MacOS specific

1. Grab yourself a Brew at http://brew.sh/
2. Get the newest python or python3 version: `brew install python`
3. Have the system prefer brew python over system python: `echo export PATH='/usr/local/bin:$PATH' >> ~/.bash_profile`  - 
4. Get z3: `brew install homebrew/science/z3`
5. Clone this repository: `git clone https://github.com/thomasjball/PyExZ3.git` 
6. Set the PATH: `. PyExZ3/setup.sh`  (do not run the setup script in a subshell `./ PyExZ3/`)
