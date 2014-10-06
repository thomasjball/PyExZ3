# Copyright: see copyright.txt

class FunctionInvocation:
	def __init__(self, function, reset):
		self.function = function
		self.reset = reset
		self.arg_constructor = {}
		self.initial_value = {}

	def callFunction(self,args):
		self.reset()
		return self.function(**args)

	def addArgumentConstructor(self, name, init, constructor):
		self.initial_value[name] = init
		self.arg_constructor[name] = constructor

	def getNames(self):
		return self.arg_constructor.keys()

	def createArgumentValue(self,name,val=None):
		if val == None:
			return self.arg_constructor[name](name,self.initial_value[name])
		else:
			return self.arg_constructor[name](name,val)

	

