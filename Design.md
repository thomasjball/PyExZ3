Design
======

FunctionInvocation
ConcolicEngine

- PythonTracer: trace the concrete execution of a Python function
	- What is a trace?
	- PythonContext
	- ByteCodeParser
	- Ignore: to make sure only code we care about is traced

- SymbolicInterpreter
	- GenericOpCode
		- LocalReference
		- GlobalReference
		- Attribute
		- ConditionalJump
		- Jump
		- FunctionCall
		- ConstantValue
		- UnaryOperator
		- BinaryOperator
		- Assignment
		- Subscr
		- ReturnValue
		- BuildList
		- PrintItem
		- SetupLoop
		- GetIterator
		- ForLoop
		- BreakLoop
	- Predicate
	- Constraint