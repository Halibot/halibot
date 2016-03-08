#
# Loader class
#   Handles loading of items (namely modules or agents)
#

import os
import imp
import inspect
import json
import logging

class Loader():

	def __init__(self, paths, superclass):
		self.items = {}
		self.paths = paths
		self.superclass = superclass
		self.log = logging.getLogger(self.__class__.__name__)

	# Finds the basepath (directory path) of an item
	def _find(self, name):
		for path in self.paths:
			found = path + os.sep + name + os.sep
			config = found + "config.json"

			if os.path.isfile(config):
				return found

		raise Exception("Could not find module/agent '" + name + "'!");

	# Loads an items into the items array
	def _load(self, name):
		basepath = self._find(name)
		supername = self.superclass.__name__

		with open(basepath + "config.json", "r") as f:
			# TODO something more with this
			config = json.loads(f.read())

		src = basepath + config["main"]

		try:
			pymod = imp.load_source(name, src)
		except Exception as e:
			self.log.warning(e)
			return False

		for objname, obj in inspect.getmembers(pymod):
			if inspect.isclass(obj) and issubclass(obj, self.superclass) and objname != supername:
				# TODO handle multiple superclasses per python module somehow?
				self.items[name] = obj
				return

		self.log.error("Could not find a " + supername + " in '" + src + "'!")
		return False

	# Returns an item by name, loads it if not loaded
	def get(self, name):
		if not name in self.items:
			self._load(name)
		return self.items[name]
