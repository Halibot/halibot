#
# Main bot class
#    Handles routing, config, agent/module loading
#
import json
import threading
import imp
import inspect
import os
from halmodule import HalModule
from halagent import HalAgent
import sys
sys.path.append(".")
#from asyncio import Queue
from queue import Queue

# This will find a path to a module/agent
#  name - the name of the module/agent
#  paths - the path list to search
def find_basepath(name, paths):
	for path in paths:
		found = path + os.sep + name + os.sep
		config = found + "config.json"

		if os.path.isfile(config):
			return found

	raise Exception("Could not find module/agent '" + name + "'!");

# Loads a module or agent class
#  name - the name of the item to load
#  paths - the paths to search for the item to load
#  superclass - the superclass required for things to subclass
#  dest - the dict to add the class object to
def load_item(name, paths, superclass, dest):
	basepath = find_basepath(name, paths)
	supername = superclass.__name__

	with open(basepath + "config.json", "r") as f:
		# TODO something more with this
		config = json.loads(f.read())

	src = basepath + config["main"]

	try:
		pymod = imp.load_source(name, src)
	except Exception as e:
		print(e)
		return False

	for objname, obj in inspect.getmembers(pymod):
		if inspect.isclass(obj) and issubclass(obj, superclass) and objname != supername:
			# TODO handle multiple superclasses per python module somehow?
			dest[name] = obj
			return

	raise Exception("Could not find a " + supername + " in '" + src + "'!")

class Halibot():

	config = {}
	agents = {}
	modules = {}
	agent_classes = {}
	module_classes = {}
	queue = None
	
	def __init__(self):
		self.queue = Queue()

	# Start the Hal instance
	def start(self, block=True):

		self._load_config()
		self._instantiate_agents()
		self._instantiate_modules()

		self._start_route()

	def _load_config(self):
		with open("config.json","r") as f:
			self.config = json.loads(f.read())

			self.module_path = self.config["module-path"]
			self.agent_path = self.config["agent-path"]

	def _instantiate_agents(self):
		inst = self.config["agent-instances"]

		for k in inst.keys():
			# TODO include directive

			conf = inst[k]
			conf["name"] = k
			of = conf["of"]

			if not of in self.agent_classes:
				self._load_agent(of)

			obj = self.agent_classes[of]
			self.agents[k] = obj(self, conf)
			self.agents[k].init()
			print("Instantiated agent '" + k + "'")

	def _instantiate_modules(self):
		inst = self.config["module-instances"]

		for k in inst.keys():
			# TODO include directive

			conf = inst[k]
			conf["name"] = k
			of = conf["of"]

			if not of in self.module_classes:
				self._load_module(of)

			obj = self.module_classes[of]
			self.modules[k] = obj(self, conf)
			self.modules[k].init()
			print("Instantiated module '" + k + "'")


	def _load_agent(self, name):
		load_item(name, self.agent_path, HalAgent, self.agent_classes)
		print("Loaded agent class '" + name + "'")

	def _load_module(self, name):
		load_item(name, self.module_path, HalModule, self.module_classes)
		print("Loaded module class '" + name + "'")


	def _start_route(self):
		t = threading.Thread(target=self._do_route)

		t.start()


	def _do_route(self):
		while True:
			m = self.queue.get(block=True)
			if m["source"] == "module":
				self.agents[m["context"]["agent"]].receive(m)
			elif m["source"] == "agent":
				for a in self.modules.values():
					a.receive(m)

	def receive(self, msg):
		self.queue.put(msg)
