TODO List
=========

- support complete set of operations on numbers
	- ensure forwarding of "builtins" to super class (hash, for example)
- support for lookup of SymbolicType in collections (and other related uses)
- need to generalize z3_wrap so we can support multiple theories for arithmetic
	- first use LIA + EUF to cover Python
	- if UNKNOWN or SAT doesn't agree with Python, then go to BitVectors
- need to handle while loops better