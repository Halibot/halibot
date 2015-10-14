#
# Main bot class
#    Handles routing, config, agent/module loading
#
import json
import threading
import sys
from halmodule import HalModule
from halagent import HalAgent
from loader import Loader
from queue import Queue,Empty

# Avoid appending "." if it i
if "." not in sys.path:
	sys.path.append(".")
import logging

class Halibot():

	config = {}
	agents = {}
	modules = {}
	queue = None

	thread = None
	running = False
	rld = False

	log = None
	
	def __init__(self):
		self.queue = Queue()
		self.log = logging.getLogger(self.__class__.__name__)

	# Start the Hal instance
	def start(self, block=True):
		self.running = True
		self._load_config()
		self._instantiate_agents()
		self._instantiate_modules()

		self._start_route()

		if block:
			self.thread.join()

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

			self.agents[k] = obj(self, conf)
			self.agents[k].name = k
			self.agents[k].init()
			self.log.info("Instantiated agent '" + k + "'")

	def _instantiate_modules(self):
		inst = self.config["module-instances"]

		for k in inst.keys():
			# TODO include directive

			conf = inst[k]

			obj = self.module_loader.get(conf["of"])

			self.modules[k] = obj(self, conf)
			self.modules[k].name = k
			self.modules[k].init()
			self.log.info("Instantiated module '" + k + "'")


	def _start_route(self):
		self.thread = threading.Thread(target=self._do_route)

		self.thread.start()


	def _do_route(self):
		while self.running:
			try:
				m = self.queue.get(block=True, timeout=5)
			except Empty:
				continue

			if m["source"] == "module":
				self.agents[m["context"]["agent"]].receive(m)
			elif m["source"] == "agent":
				for a in self.modules.values():
					a.receive(m)

	def receive(self, msg):
		self.queue.put(msg)
