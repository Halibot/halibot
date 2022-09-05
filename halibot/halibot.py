#
# Main bot class
#    Handles routing, config, agent/module loading
#
import json
import threading
import asyncio
import os, sys
import importlib
import collections
import halibot.packages
try:
	from packaging.version import Version
except:
	from distutils.version import StrictVersion as Version
from queue import Queue,Empty
from string import Template
from .halmodule import HalModule
from .halagent import HalAgent
from .halauth import HalAuth

# Avoid appending "." if it i
if "." not in sys.path:
	sys.path.append(".")
import logging

HALDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class ObjectDict(dict):

	@property
	def modules(self):
		return dict(filter(lambda x: isinstance(x[1], HalModule), self.items()))

	@property
	def agents(self):
		return dict(filter(lambda x: isinstance(x[1], HalAgent), self.items()))

#
# This class represents the hierarchy of config files
#
class Config(collections.abc.MutableMapping):

	def __init__(self):
		self.local = {}
		self.system = {}

	def _load_config(self, workdir="."):
		# Special values expanded inside of configs
		specials = {
			'HALDIR': HALDIR
		}

		with open(os.path.join(workdir, "config.json"), "r") as f:
			text = Template(f.read()).safe_substitute(**specials)
			self.set_local(json.loads(text))

		try:
			with open(os.path.join(HALDIR, "config", "system.json")) as f:
				text = Template(f.read()).safe_substitute(**specials)
				self.set_system(json.loads(text))
		except FileNotFoundError as _:
			self.log.info("No system config loaded.")

	def _write_config(self, workdir="."):
		with open(os.path.join(workdir, "config.json"), "w") as f:
			f.write(json.dumps(self.local, sort_keys=True, indent=4))

	def _refresh_packages(self):
		lpath = self.local.get("package-path", [])
		spath = self.system.get("package-path", [])
		halibot.packages.__path__ = lpath + spath

	def set_local(self, local):
		self.local = local
		self._refresh_packages()

	def set_system(self, system):
		self.system = system
		self._refresh_packages()

	def __getitem__(self, key):
		if key in self.local: return self.local[key]
		return self.system[key]

	def __setitem__(self, key, value):
		self.local[key] = value

	def __delitem__(self, key):
		del self.local[value]

	def __iter__(self):
		return iter(self.local.keys() + self.system.keys())

	def __len__(self):
		return len(set(self.local.keys()) + set(self.system.keys()))

	def __keytransform__(self, key):
		return key

class Halibot():

	VERSION = "0.2.0"

	running = False
	log = None

	def __init__(self, **kwargs):
		self.log = logging.getLogger(self.__class__.__name__)

		self.use_config = kwargs.get("use_config", True)
		self.workdir = kwargs.get("workdir", ".")

		self.auth = HalAuth()
		self.objects = ObjectDict()
		self.config = Config()

		self.eventloop = asyncio.SelectorEventLoop()
		self._thread = None

	# Start the Hal instance
	def start(self, block=True):
		self.running = True

		if self.use_config:
			self.config._load_config()
			self._instantiate_objects("agent")
			self._instantiate_objects("module")
			self._instantiate_objects("filter")
			if self.config.get("use-auth", False):
				self.auth.load_perms(self.config.get("auth-path","permissions.json"))

		if block:
			self.eventloop.run_forever()
			self.eventloop.close()
		else:
			self._thread = threading.Thread(target=self._block_forever)
			self._thread.start()

	def _block_forever(self):
		self.eventloop.run_forever()
		self.eventloop.close()

	def shutdown(self):
		self.log.info("Shutting down halibot...")
		for o in self.objects.values():
			o._shutdown()

		self.eventloop.call_soon_threadsafe(self.eventloop.stop)
		self.log.info("Halibot shutdown. Threads left: " + str(threading.active_count()))
		if self._thread:
			self._thread.join()

		self.running = False

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
		inst.log.name += "({})".format(name)
		try:
			inst.init()
		except Exception as e:
			self.log.error(f"Failed to instantiate object '{name}': {e}")
		else:
			self.log.info("Instantiated object '" + name + "'")

	def _load_config(self):
		self.config._load_config(workdir=self.workdir)

	def _write_config(self):
		self.config._write_config(workdir=self.workdir)

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
		inst = self.config.get(key + "-instances", {})

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
