# Copyright: see copyright.txt

# symbolic tainting starts at FunctionInvocation by adding a symbolic parameter
# via the method addSymbolicParameter with a subclass of SymbolicType
# see loader.py for example of setting it up

class FunctionInvocation:
	def __init__(self, function):
		self.function = function
		self.symbolic_inputs = {}  # string -> SymbolicType
		self.symbolic_constructor = {}

	def addSymbolicParameter(self, name, constructor, val):
		self.symbolic_constructor[name] = constructor
		self.symbolic_inputs[name] = constructor(name,val)

	def updateSymbolicParameter(self, name, val):
		self.symbolic_inputs[name] = self.symbolic_constructor[name](name,val)


