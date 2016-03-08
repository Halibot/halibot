#
# Main bot class
#    Handles routing, config, agent/module loading
#
import json
import threading
import sys
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

			self.agent_loader = Loader(self.config["agent-path"], HalAgent)
			self.module_loader = Loader(self.config["module-path"], HalModule)

	def _instantiate_agents(self):
		inst = self.config["agent-instances"]

		for k in inst.keys():
			# TODO include directive

			conf = inst[k]
			obj = self.agent_loader.get(conf["of"])

			self.add_agent_instance(k, obj(self, conf))

	def _instantiate_modules(self):
		inst = self.config["module-instances"]

		for k in inst.keys():
			# TODO include directive

			conf = inst[k]
			obj = self.module_loader.get(conf["of"])

			self.add_module_instance(k, obj(self, conf))

	def get_object(self, name):
		# TODO priority?
		if name in self.modules: return self.modules[name]
		if name in self.agents: return self.agents[name]
		return None

	# Reload a class, and restart all modules of that class
	#  name: Class name, should match halmodule class name
	def reload_class(self, name):
		for ld in (self.agent_loader, self.module_loader):
			if ld.remove(name):
				log.debug.info("Removed loaded class: '{}'".format(name))
				obj = self.module_loader.get(name)
				for o in self.modules.items():
					if o[1].__class__.__name__ == obj.__name__:
						o[1]._shutdown()
						conf = o[1].config
						self.add_module_instance(o[0], obj(self, conf))

	# Restart a module instance by name
	def restart(self, name):
		o = self.get_object(name)
		if o:
			o.shutdown()
			o.init()
		else:
			self.log.warning("Failed to restart instance '{}'".format(name))
