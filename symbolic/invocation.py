# Copyright: see copyright.txt

# symbolic tainting starts at FunctionInvocation by adding a symbolic parameter
# via the method addSymbolicParameter with a subclass of SymbolicType
# see loader.py for example of setting it up

class FunctionInvocation:
	def __init__(self, function, reset):
		self.function = function
		self.reset = reset
		self.symbolic_constructor = {}

	def callFunction(self,args):
		self.reset()
		return self.function(**args)

	def addSymbolicParameter(self, name, constructor):
		self.symbolic_constructor[name] = constructor

	def getNames(self):
		return self.symbolic_constructor.keys()

	def createParameterValue(self,name,val):
		return self.symbolic_constructor[name](name,val)

	

