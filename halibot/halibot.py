#
# Main bot class
#    Handles routing, config, agent/module loading
#
import json
import threading
import os, sys
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
		self.routing = HalRoute(self)

	# Start the Hal instance
	def start(self, block=True):
		self.running = True

		if self.use_config:
			self._load_config()
			self._instantiate_objects("agent")
			self._instantiate_objects("module")
			if self.use_auth:
				self.auth.load_perms(self.config.get("auth-path","permissions.json"))

		self.routing.compile()

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

class HalRoute():

	class Route():
		def __init__(self, pattern, targets):
			self.reg = re.compile(pattern)
			self.pattern = pattern
			self.target = target

		def match(self, string):
			return self.reg.match(string)

	def __init__(self, hal):
		self.hal = hal
		self.lookup = []
		self.passive = {}
		self.active = {}

	# Compile a "routing" config object to a lookup table
	#  Unless data= is set, it loads from config. If the config key isn't set, uses the default
	def compile(self, data=None):
		if not data:
			data = self.hal.config.get("routing", {"table": [".* -> $default"], "containers": {}})

		self.lookup = []
		self.passive = { c[0]:c[1]["contains"] for c in data["containers"].items() if "using" not in c[1].keys() }
		self.active = { c[0]:c[1]["contains"] for c in data["containers"].items() if "using" in c[1].keys() }

		for a in data["table"]:
			# TODO: validate ahead of time probably
			s,t = a.split(" -> ")
			self.lookup.append(Route(s, t))

	# Returns a list of targets to send to based on source RI, this is pre-resolved
	#  This should probably be used for handling send_to() targets
	def get(self, ri):
		for r in self.lookup:
			if r.match(ri):
				return self.resolve(r.target)
		return []

	# Add a route to the top of the table
	def add(self, sreg, target):
		self.lookup.insert(0, Route(sreg, target))

	# Append a route to the end of the table
	def append(self, sreg, target):
		self.lookup.append(Route(sreg, target))

	# Resolve a name to a list of targets, if the name is a passive container
	def resolve(self, name):
		if name not in self.passive.keys():
			# Special case the "default" container to be all modules, if not overridden
			if name == "$default":
				return self.hal.objects.modules.keys()
			return [ name ]

		ret = []
		# Recursively resolve nested passive containers
		for t in self.passive[name]:
			ret += self.resolve(t)

		return ret

	# Similar to resolve(), but also resolves active containers
	#  Use this to determine if a module is ever to be seen by a message from a particular origin RI
	def flatten(self, name):
		# Clear passive containers first
		ls = self.resolve(name)

		ret = []
		for r in ls:
			tmp = self.active.get(r, None)
			if tmp:
				for t in tmp["contains"]:
					# Flatten active's children/resolve passives before adding
					ret += self.flatten(t)
			else:
				# Not an active container, pass it through
				ret.append(r)

	# Write out a dictionary of what the "routing" key should be
	def serialize_config(self):
		ret = {}

		ls = []
		for l in self.lookup:
			ls.append("{} -> {}".format(l.pattern, l.target))

		ct = {}
		for i in self.passive.items():
			ct[i[0]] = {"contains": i[1]}
		# TODO: actives, since they weird yo

		ret["table"] = ls
		ret["containers"] = ct

		return ret
