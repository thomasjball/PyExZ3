#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   -  Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   -  Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#   -  Neither the names of the contributors, nor their associated universities or
#      organizations may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import time

class Statistics:
	def __init__(self):
		self.ts_stack = []
		self.profiles = {}
		self.counters = {}

	def pushProfile(self, name):
		t = (name, time.clock(), time.time())
		self.ts_stack.append(t)

	def popProfile(self):
		t = self.ts_stack.pop()
		tdiff = {}
		tdiff["cpuc"] = time.clock() - t[1]
		tdiff["wallc"] = time.time() - t[2]
		tdiff["samples"] = 1
		tdiff["cpuc_max"] = tdiff["cpuc"]
		tdiff["cpuc_min"] = tdiff["cpuc"]
		tdiff["wallc_max"] = tdiff["wallc"]
		tdiff["wallc_min"] = tdiff["wallc"]
		tdiff["total_cpu"] = tdiff["cpuc"]
		tdiff["total_wall"] = tdiff["wallc"]

		if self.profiles.has_key(t[0]):
			tavg = self.profiles[t[0]]
			tavg["wallc"] = (tdiff["wallc"] + tavg["samples"]*tavg["wallc"]) / (tavg["samples"] + 1)
			tavg["cpuc"] = (tdiff["cpuc"] + tavg["samples"]*tavg["cpuc"]) / (tavg["samples"] + 1)
			if tdiff["cpuc"] > tavg["cpuc_max"]:
				tavg["cpuc_max"] = tdiff["cpuc"]
			if tdiff["cpuc"] < tavg["cpuc_min"]:
				tavg["cpuc_min"] = tdiff["cpuc"]
			if tdiff["wallc"] > tavg["wallc_max"]:
				tavg["wallc_max"] = tdiff["wallc"]
			if tdiff["wallc"] < tavg["wallc_min"]:
				tavg["wallc_min"] = tdiff["wallc"]
			tavg["samples"] += 1
			tavg["total_cpu"] += tdiff["total_cpu"]
			tavg["total_wall"] += tdiff["total_wall"]
			self.profiles[t[0]] = tavg
		else:
			self.profiles[t[0]] = tdiff

	def getProfilingOutput(self):
		keys = self.profiles.keys()
		keys.sort()
		s = "  measurement name  |   samples   |   wclock avg   |   wclock tot   |   wclock max   |    CPU tot\n"
		for k in keys:
			p = self.profiles[k]
			name = k.center(20)
			samples = str(p["samples"]).center(13)
			wallc = "%.3f" % p["wallc"]
			wallc = wallc.center(16)
			wallc_tot = "%.3f" % p["total_wall"]
			wallc_tot = wallc_tot.center(16)
			wallc_max = "%.3f" % p["wallc_max"]
			wallc_max = wallc_max.center(16)
			cpuc = "%.3f" % p["cpuc"]
			cpuc = cpuc.center(16)
			cpuc_tot = "%.3f" % p["total_cpu"]
			cpuc_tot = cpuc_tot.center(16)
			cpuc_max = "%.3f" % p["cpuc_max"]
			cpuc_max = cpuc_max.center(16)
			s += "%s|%s|%s|%s|%s|%s\n" % (name, samples, wallc, wallc_tot, wallc_max, cpuc_tot)
		return s

	def newCounter(self, name):
		if name not in self.counters:
			self.counters[name] = 0

	def incCounter(self, name):
		self.counters[name] += 1

	def getCounterOutput(self):
		keys = self.counters.keys()
		keys.sort()
		s = ""
		for k in keys:
			s += "%s: %d\n" % (k, self.counters[k])
		return s

	def reset(self):
		self.ts_stack = []
		self.profiles = {}
		self.counters = {}

stats = Statistics()

def getStats():
	return stats

