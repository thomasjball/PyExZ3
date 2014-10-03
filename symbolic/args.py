def symbolic(**arg_types):
	def decorator(f):
		f.symbolic_args = arg_types
		return f
	return decorator

def concrete(**arg_types):
	def decorator(f):
		f.concrete_args = arg_types
		return f
	return decorator
