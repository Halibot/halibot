#
# Main bot class
#    Handles routing, config, agent/module loading
#
import json
import threading
from halmodule import HalModule
from halagent import HalAgent
from loader import Loader
import sys
sys.path.append(".")
#from asyncio import Queue
from queue import Queue

class Halibot():

	config = {}
	agents = {}
	modules = {}
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

			self.agent_loader = Loader(self.config["agent-path"], HalAgent)
			self.module_loader = Loader(self.config["module-path"], HalModule)

	def _instantiate_agents(self):
		inst = self.config["agent-instances"]

		for k in inst.keys():
			# TODO include directive

			conf = inst[k]
			conf["name"] = k

			obj = self.agent_loader.get(conf["of"])

			self.agents[k] = obj(self, conf)
			self.agents[k].init()
			print("Instantiated agent '" + k + "'")

	def _instantiate_modules(self):
		inst = self.config["module-instances"]

		for k in inst.keys():
			# TODO include directive

			conf = inst[k]
			conf["name"] = k

			obj = self.module_loader.get(conf["of"])

			self.modules[k] = obj(self, conf)
			self.modules[k].init()
			print("Instantiated module '" + k + "'")


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
