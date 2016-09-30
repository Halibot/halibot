#
# Main bot class
#    Handles routing, config, agent/module loading
#
import json
import threading
import sys, importlib
from queue import Queue,Empty
from .halmodule import HalModule
from .halagent import HalAgent
from .loader import Loader

# Avoid appending "." if it i
if "." not in sys.path:
	sys.path.append(".")
import logging

class Halibot():

	config = {}
	agents = {}
	modules = {}

	running = False
	log = None

	def __init__(self, **kwargs):
		self.log = logging.getLogger(self.__class__.__name__)

		self.use_config = kwargs.get("use_config", True)

	# Start the Hal instance
	def start(self, block=True):
		self.running = True

		if self.use_config:
			self._load_config()
			self._instantiate_agents()
			self._instantiate_modules()

	def shutdown(self):
		self.log.info("Shutting down halibot...");

		for m in self.modules.values():
			m._shutdown()
		for a in self.agents.values():
			a._shutdown()

		self.log.info("Halibot shutdown. Threads left: " + str(threading.active_count()))

	def add_agent_instance(self, name, inst):
		self.agents[name] = inst
		inst.name = name
		inst.init()
		self.log.info("Instantiated agent '" + name + "'")

	def add_module_instance(self, name, inst):
		self.modules[name] = inst
		inst.name = name
		inst.init()
		self.log.info("Instantiated module '" + name + "'")

	def _load_config(self):
		with open("config.json","r") as f:
			self.config = json.loads(f.read())

			# Deprecated; remove with 1.0
			self.agent_loader = Loader(self.config["package-path"], HalAgent)
			self.module_loader = Loader(self.config["package-path"], HalModule)


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

	def _instantiate_agents(self):
		inst = self.config["agent-instances"]

		for k in inst.keys():
			# TODO include directive

			conf = inst[k]
			split = conf["of"].split(":")

			if len(split) == 1:
				# deprecated; remove with 1.0
				obj = self.agent_loader.get(conf["of"])
			elif len(split) == 2:
				obj = self._get_class_from_package(split[0], split[1])
			else:
				self.log.error("Invalid class identifier {}, must contain only 1 ':'".format(conf["of"]))
				continue

			self.add_agent_instance(k, obj(self, conf))

	def _instantiate_modules(self):
		inst = self.config["module-instances"]

		for k in inst.keys():
			# TODO include directive

			conf = inst[k]
			split = conf["of"].split(":")

			if len(split) == 1:
				# deprecated; remove with 1.0
				obj = self.module_loader.get(conf["of"])
			elif len(split) == 2:
				obj = self._get_class_from_package(split[0], split[1])
			else:
				self.log.error("Invalid class identifier {}, must contain only 1 ':'".format(conf["of"]))
				continue

			self.add_module_instance(k, obj(self, conf))

	def get_object(self, name):
		# TODO priority?
		if name in self.modules: return self.modules[name]
		if name in self.agents: return self.agents[name]
		return None

	def get_package(self, name):
		for p in self.config['package-path']:
			path = p.replace('/', '.') + '.' + name.replace('/', '.')
			print(path)
			mod = importlib.import_module(path)
			if mod != None:
				return mod
		return None

	# TODO: Reload a class, and restart all modules of that class
	def reload(self, cls):
		pass

	# Restart a module instance by name
	def restart(self, name):
		o = self.get_object(name)
		if o:
			o.shutdown()
			o.init()
		else:
			self.log.warning("Failed to restart instance '{}'".format(name))
