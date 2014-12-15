PyExZ3
======

###Python Exploration with Z3

This code is a substantial rewrite of the NICE project's
(http://code.google.com/p/nice-of/) symbolic execution engine for
Python, now using the Z3 theorem prover (http://z3.codeplex.com). We have
removed the NICE-specific dependences, platform-specific code, and
made various improvements, documented below, so it can be used
by anyone wanting to experiment with dynamic symbolic execution.

In the limit, **PyExZ3** attempts to *explore* all the feasible paths in a
Python function by:
- executing the function on a concrete input to trace a path through the control flow of the function;
- symbolic executing the path to determine how its conditions depend on the function's input parameters;
- generating new values for the parameters to drive the function to yet uncovered paths, using Z3.  

For small programs without loops or recursion, 
**PyExZ3** may be able to explore all feasible paths.

A novel aspect of the rewrite is to rely solely on Python's operator
overloading to accomplish all the interception needed for symbolic
execution; no AST rewriting or bytecode instrumentation is required,
This significantly improves the robustness and portability of **PyExZ3**, 
as well as reducing its size.

###Setup instructions:

- Make sure that you use Python 32-bit (64-bit) if-and-only-if you use the Z3 32-bit (64-bit) binaries. 
Testing so far has been on Python 3.2.3 and 32-bit.
- Install Python 3.2.3 (https://www.python.org/download/releases/3.2.3/)
- Install the latest "unstable" release of Z3 to directory Z3HOME from http://z3.codeplex.com/releases
(click on the "Planned" link on the right to get the latest binaries for all platforms)
- Add Z3HOME\bin to PATH and PYTHONPATH
- MacOS: setup.sh for Homebrew default locations for Python and Z3; see end for MacOS specific instructions
- Optional:
-- install GraphViz utilities (http://graphviz.org/)

### Check that everything works:

- `python run_tests.py test` should pass all tests

- `python pyexz3.py test\FILE.py` to run a single test from the test directory

### Usage of PyExZ3

- **Basic usage**: give a Python file `FILE.py` as input. By default, `pyexz3` expects `FILE.py` 
to contain a function named `FILE` where symbolic execution will start:

  - `pyexz3 FILE.py`

- **Starting function**: You can override the default starting function with `--start MAIN`,
where `MAIN` is the name of a  function in `FILE`: 

  - pyexz3 `--start=MAIN` FILE.py

- **Bounding the number of iterations** of the path exploration is essential when
analyzing functions with loops and/or recursion. Specify a bound using the `max-iters` flag:

  - pyexz3 `--max-iters=42` FILE.py

- **Arguments to starting function**: by default, pyexz3 associates a symbolic integer
(with initial value 0) for each parameter of the starting function. Import from
`symbolic.args` to get the `@concrete` and `@symbolic` decorators that let you override
the defaults on the starting function:
  ```
from symbolic.args import *

@concrete(a=1,b=2)
@symbolic(c=3)
def startingfun(a,b,c,d):
    ...
  ```
  The `@concrete` decorator declares that a parameter will not be treated symbolically and
provides an initial value for the parameter.
The `@symbolic` decorator declares that a parameter will be treated symbolically - the type 
of the associated initial value for the argument will be used to determine the proper symbolic 
type  (if one exists).   In the above example, parameters `a` and `b` are treated concretely
and will have initial values `1` and `2` (for all paths explored), and parameter `c` will 
be treated as a symbolic integer input with the initial value `3` (its value can change after
first path has been explored). Since parameter `d` is not specified, it will be treated as a symbolic 
integer input with the initial value 0:

- **Output**: `pyexz3` prints the list of generated inputs and corresponding observed 
return values to standard out; the lists of generated inputs and the corresponding return values are
returned by the exploration engine to `pyexz3` where they can be used for other 
purposes, as described below.

- **Expected result functions** are used for testing of `pyexz3`. If the `FILE.py` contains a function named `expected_result` then after path exploration is complete, the list of return values will be compared against the list 
returned by `expected_result`. More precisely, the two lists are converted into bags and the bags compared for equality. If a function named `expected_result_set` is present instead, the list are converted into sets and the sets are
compared for equality.  List equality is too strong a criteria for testing, since small changes to programs can lead to paths being explored in different orders. 

- **Import behavior**: the location of the `FILE.py` is added to the import path so that all imports in `FILE.py` 
relative to that file will work.

- **Other options**
  - `--graph=DOTFILE`
  - `--log=LOGFILE`

### MacOS specific

1. Grab yourself a Brew at http://brew.sh/
2. Get the newest python or python3 version: `brew install python`
3. Have the system prefer brew python over system python: `echo export PATH='/usr/local/bin:$PATH' >> ~/.bash_profile`  - 
4. Get z3: `brew install homebrew/science/z3`
5. Clone this repository: `git clone https://github.com/thomasjball/PyExZ3.git` 
6. Set the PATH: `. PyExZ3/setup.sh`  (do not run the setup script in a subshell `./ PyExZ3/`)

### Vagrant specific

[Vagrant](http://www.vagrantup.com/) is a cross-platform tool to manage
virtualized development environments. Vagrant runs on Windows, OS X, and
Linux and can manage virtual machines running on VirtualBox, VMware,
Docker, and Hyper-V.

1. [Download Vagrant](http://www.vagrantup.com/downloads.html).
2. Install [VirtualBox](https://www.virtualbox.org/) or configure an
[alternative
provider](http://docs.vagrantup.com/v2/providers/index.html).
3. Run `vagrant up` from the PyExZ3 directory. The Vagrantfile in the
repository tells Vagrant to download a Debian base image, launch it with
the default provider (VirtualBox), and run the script `vagrant.sh` to
provision the machine.
4. Once the provisioning is done you can SSH into the machine using
`vagrant ssh` and PyExZ3 is ready to run. Please note that the
provisioning takes a while as Git is compiled from source as Debian's
Git is incompatible with [CodePlex](http://www.codeplex.com/) where Z3
is hosted.

### CVC SMT Solver

By default PyExZ3 uses the Z3 to solve path predicates. Optionally, the 
[CVC SMT](http://cvc4.cs.nyu.edu/web/) solver can be enabled with the 
`--cvc` argument. While the two solvers offer a similar feature set, the 
integration of CVC differs from Z3 in a number of ways. Most 
predominately, the CVC integration uses an unbounded rational number 
representation for Python numbers, converting back and forth to 
bitvectors only in the presence of bitwise operations. The Z3 
integration uses bounded bitvectors for generating inputs of all 
numbers. For programs that use any significant number of bitwise 
operations, the default Z3-based configuration is strongly recommended.
