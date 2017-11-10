#
# Main bot class
#    Handles routing, config, agent/module loading
#
import json
import threading
import os, sys, re
import importlib
import halibot.packages
from distutils.version import StrictVersion as Version
from queue import Queue,Empty
from .halmodule import HalModule
from .halagent import HalAgent
from .halauth import HalAuth

# Avoid appending "." if it i
if "." not in sys.path:
	sys.path.append(".")
import logging

class ObjectDict(dict):

	@property
	def modules(self):
		return dict(filter(lambda x: isinstance(x[1], HalModule), self.items()))

	@property
	def agents(self):
		return dict(filter(lambda x: isinstance(x[1], HalAgent), self.items()))


class Halibot():

	VERSION = "0.2.0"

	config = {}

	running = False
	log = None

	def __init__(self, **kwargs):
		self.log = logging.getLogger(self.__class__.__name__)

		self.use_config = kwargs.get("use_config", True)
		self.use_auth = kwargs.get("use_auth", True)
		self.workdir = kwargs.get("workdir", ".")

		self.auth = HalAuth()
		self.objects = ObjectDict()

	# Start the Hal instance
	def start(self, block=True):
		self.running = True

		if self.use_config:
			self._load_config()
			self._instantiate_objects("agent")
			self._instantiate_objects("module")
			if self.use_auth:
				self.auth.load_perms(self.config.get("auth-path","permissions.json"))

	def shutdown(self):
		self.log.info("Shutting down halibot...");

		for o in self.objects.values():
			o._shutdown()

		self.log.info("Halibot shutdown. Threads left: " + str(threading.active_count()))

	def _check_version(self, obj):
		v = Version(self.VERSION)
		if not hasattr(obj, "HAL_MINIMUM"):
			self.log.warn("Module class '{}' does not define a minimum version, trying to load anyway...".format(obj.__class__.__name__))
			return True

		if v < Version(obj.HAL_MINIMUM):
			self.log.error("Rejecting load of '{}', requires minimum Halibot version '{}'. (Currently running '{}')".format(obj.__class__.__name__, obj.HAL_MINIMUM, self.VERSION))
			return False

		if hasattr(obj, "HAL_MAXIMUM"):
			if v >= Version(obj.HAL_MAXIMUM):
				self.log.error("Rejecting load of '{}', requires maximum Halibot version '{}'. (Currently running '{}')".format(obj.__class__.__name__, obj.HAL_MAXIMUM, self.VERSION))
				return False
		return True

	def add_instance(self, name, inst):
		self.objects[name] = inst
		inst.name = name
		inst.init()
		self.log.info("Instantiated object '" + name + "'")

	def _load_config(self):
		with open(os.path.join(self.workdir, "config.json"), "r") as f:
			self.config = json.loads(f.read())
			halibot.packages.__path__ = self.config.get("package-path", [])

	def _write_config(self):
		with open(os.path.join(self.workdir, "config.json"), "w") as f:
			f.write(json.dumps(self.config, sort_keys=True, indent=4))


	def _get_class_from_package(self, pkgname, clsname):
		pkg = self.get_package(pkgname)
		if pkg == None:
			self.log.error("Cannot find package {}!".format(pkgname))
			return None

		obj = getattr(pkg, clsname, None)
		if obj == None:
			self.log.error("Cannot find class {} in package {}!".format(clsname, pkgname))
			return None

		return obj

	# Load a halobject from a package descriptor (e.g. hello:Hello), but does NOT
	#  start or add it to the current instance.
	def load_object(self, pkg, conf={}):
			split = pkg.split(":")

			if len(split) == 2:
				obj = self._get_class_from_package(*split)
				if obj and self._check_version(obj):
						return obj(self, conf=conf)
			else:
				self.log.error("Invalid class identifier {}, must contain only 1 ':'".format(conf["of"]))
			return None

	def _instantiate_objects(self, key):
		inst = self.config[key + "-instances"]

		for k in inst.keys():
			conf = inst[k]
			obj = self.load_object(conf["of"], conf=conf)

			if obj:
				self.add_instance(k, obj)

	def get_package(self, name):
		return importlib.import_module('halibot.packages.' + name)

	def reload(self, name):
		parent = 'halibot.packages.' + name
		for k,o in self.objects.items():
			if o.__module__.startswith(parent + '.') or o.__module__ == parent:
				o._shutdown()
				mod = importlib.reload(importlib.import_module(o.__module__))
				cls = getattr(mod, o.__class__.__name__)
				self.add_instance(k, cls(self, o.config))

	# Restart a module instance by name
	def restart(self, name):
		o = self.objects.get(name)
		if o:
			o.shutdown()
			o.init()
		else:
			self.log.warning("Failed to restart instance '{}'".format(name))

	# Given a source RI, return a list of routed destinations
	#
	# Normally, active containers (with a name prrefixed with @ and an object defined
	# under that name) are not resolved, but for the purposes of seeing where messages'
	# final destinations are, then can be forced to resolve with resolve_all=True. This
	# option should not be used for actually sending messages.
	def route(self, source, resolve_all=False):
		for d in self.config.get('routes', []):
			dest = []
			found = False

			# Find all matching patterns of the same precedence level
			for pat in d:
				if re.match(pat, source):
					# Found a match
					found = True
					raw = d[pat] if type(d[pat]) == list else [ d[pat] ]
					for ri in raw:
						name = ri.split('/')[0]
						if ri.startswith('@') and (resolve_all or not name in self.objects):
							# Resolve aliases
							dest.extend(self.route(ri))
						else:
							dest.append(ri)
			if found:
				return dest

		return []

	# Add a route to the config
	def add_route(self, src, dest):
		if type(dest) != list: dest = [ dest ]

		if len(self.config.get('routes', [])) > 0:
			self.config['routes'][0][src] = self.config['routes'][0].get(src, []) + dest
		else:
			self.config['routes'] = [ { src: dest } ]
