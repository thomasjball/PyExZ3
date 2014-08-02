# Copyright: see copyright.txt

class SymbolicDictionary(dict):
	def __init__(self, *args, **kwargs):
		dict.__init__(self)
		self.update(*args, **kwargs)

	def has_key(self, key):
		for k in self.keys():
			if k == key:
				return True
		return False

