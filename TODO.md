TODO List
=========

- add basic support for SymbolicDictionary
- need to capture exceptions thrown by code under test as test results
- interesting question arises about re-initialization of input arguments
by ExplorationEngine and re-import of module under test in the face of
mutable initial objects - we want the re-import to be done before the 
re-initialization, but that's not how it currently works. Easiest thing
to do is only allow empty dictionary to be specified in @symbolic
- check input/output behavior separately from sym_exe
- use consist case on names (Caml or C, choose one)


