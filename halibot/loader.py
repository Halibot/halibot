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

	# TODO: Fully deprecate this with the new package format
	def _load_legacy(self, name, basepath, supername, config):
		src = basepath + config["main"]

		try:
			pymod = imp.load_source(name, src)
		except Exception as e:
			self.log.warning(e)
			return False

		for objname, obj in inspect.getmembers(pymod):
			if inspect.isclass(obj) and issubclass(obj, self.superclass) and objname != supername:
				self.items[name] = obj
				return

		self.log.error("Could not find a " + supername + " in '" + src + "'!")
		return False

	# Loads an items into the items array
	def _load(self, name):
		basepath = self._find(name)
		supername = self.superclass.__name__

		with open(basepath + "config.json", "r") as f:
			config = json.loads(f.read())

		# Check if using the new loader format or not
		if not config.get("main"):
			self.log.error("Failed to load '{}', 'main' key not found in module config".format(name))
			return False
		elif len(config.get("main").split(":")) != 2:
			self.log.warning("New class specifier not detected, falling back to class detection-based loader")
			self._load_legacy(name, basepath, supername, config)
			return

		src,clsname = config["main"].split(":")
		src = basepath + src

		try:
			pymod = imp.load_source(name, src)
		except Exception as e:
			self.log.warning(e)
			return False

		try:
			obj = getattr(pymod,clsname)
		except:
			self.error("Module '{}' failed to load: Could not find class '{}' in '{}'".format(name, src, cls))
			return

		self.items[name] = obj


	# Returns an item by name, loads it if not loaded
	def get(self, name):
		if not name in self.items:
			self._load(name)
		return self.items[name]

	# Remove a class by name from the loaded objects dict
	#  Return the class (True) if found, otherwise None (false)
	def remove(self, name):
		if name in self.items.keys():
			return self.items.pop(name, None)
