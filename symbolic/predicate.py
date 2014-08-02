# Copyright - see copyright.txt

import logging
import utils

log = logging.getLogger("se.predicate")

class Predicate:
	"""Predicate is one specific ``if'' encountered during the program execution.
	   """
	def __init__(self, condexpr, result):
		self.expr = condexpr
		self.result = result

	def __eq__(self, other):
		if isinstance(other, Predicate):
			res = self.result == other.result and self.expr.symbolicEq(other.expr)
			return res
		else:
			return False

	def __hash__(self):
		return hash(self.expr)

	def __str__(self):
		return self.expr.toString() + " (%s)" % (self.result)

	def __repr__(self):
		return self.__str__()

	def negate(self):
		"""Negates the current predicate"""
		assert(self.result is not None)
		self.result = not self.result

