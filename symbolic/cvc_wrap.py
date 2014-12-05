# Copyright: see copyright.txt

import logging

import CVC4
from CVC4 import ExprManager, SmtEngine, Result

from .cvc_expr.integer import CVCInteger

log = logging.getLogger("se.cvc")

class CVCWrapper(object):
	def __init__(self):
		self.N = 32
		self.asserts = None
		self.query = None
		self.use_lia = True
		self.cvc_expr = None

	def findCounterexample(self, asserts, query):
		"""Tries to find a counterexample to the query while
	  	 asserts remains valid."""
		self.em = ExprManager()
		self.solver = SmtEngine(self.em)
		self.query = query
		self.asserts = self._coneOfInfluence(asserts,query)
		res = self._findModel()
		log.debug("Query -- %s" % self.query)
		log.debug("Asserts -- %s" % asserts)
		log.debug("Cone -- %s" % self.asserts)
		log.debug("Result -- %s" % res)
		return res

	# private

	# this is very inefficient
	def _coneOfInfluence(self,asserts,query):
		cone = []
		cone_vars = set(query.getVars())
		ws = [ a for a in asserts if len(set(a.getVars()) & cone_vars) > 0 ]
		remaining = [ a for a in asserts if a not in ws ]
		while len(ws) > 0:
			a = ws.pop()
			a_vars = set(a.getVars())
			cone_vars = cone_vars.union(a_vars)
			cone.append(a)
			new_ws = [ a for a in remaining if len(set(a.getVars()) & cone_vars) > 0 ]
			remaining = [ a for a in remaining if a not in new_ws ]
			ws = ws + new_ws
		return cone

	def _findModel(self):
		self.solver.push()
		self.cvc_expr = CVCInteger()
		self.cvc_expr.toCVC(self.solver,self.asserts,self.query)
		res = self.solver.checkSat()
		logging.debug("Solver returned %s" % res.toString())								
		if res == Result.UNSAT:
			ret = None
		elif res == Result.VALIDITY_UNKNOWN:
			ret = None
		else: 
			ret = self._getModel()		
		self.solver.pop()
		return ret

	def _getModel(self):
		res = {}		
		for name in self.cvc_expr.z3_vars.keys():
			try:
				ce = model.eval(self.z3_expr.z3_vars[name])
				res[name] = ce.as_signed_long()
			except:
				pass
		return res
	

