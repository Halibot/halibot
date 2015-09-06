#
# Main bot class
#    Handles routing, config, agent/module loading
#
import json
import threading
import imp
import inspect
from halmodule import HalModule
from agent import Agent
import sys
sys.path.append(".")
#from asyncio import Queue
from queue import Queue

class Halibot():

	config = {}
	agents = {}
	modules = []
	queue = None
	
	def __init__(self):
		self.queue = Queue()

	# Start the Hal instance
	def start(self, block=True):

		# TODO: Make these do things
		self._load_config()
		self._load_agents()
		self._load_modules()

		self._start_route()

	def _load_config(self):
		with open("config.json","r") as f:
			self.config = json.loads(f.read())

	# TODO: Make robust
	def _load_agents(self):
		for a in self.config["agents"]:
			self._load_agent(a)

	# TODO: Make robust
	def _load_modules(self):
		for m in self.config["modules"]:
			self._load_module(m)

	def _load_agent(self, conf):
		f, p, d = imp.find_module(conf["path"][:-3])
		inst = conf.get("name")

		try:
			agt = imp.load_module(conf["path"][:-3], f, p, d)
		except Exception as e:
			print(e)
			return False

		for name, obj in inspect.getmembers(agt):
			if inspect.isclass(obj) and issubclass(obj, Agent) and name != "Agent":
				if not inst:
					inst = name

				self.agents[inst] = obj(self, conf)
				self.agents[inst].init()

	def _load_module(self, conf):
		f, p, d = imp.find_module(conf["path"][:-3])
		inst = conf.get("name")

		try:
			mod = imp.load_module(conf["path"][:-3], f, p, d)
		except Exception as e:
			print(e)
			return False

		for name, obj in inspect.getmembers(mod):
			if inspect.isclass(obj) and issubclass(obj, HalModule) and name != "HalModule":
				self.modules.append(obj(self, conf))
				self.modules[-1].init()

	def _start_route(self):
		t = threading.Thread(target=self._do_route)

		t.start()


	def _do_route(self):
		while True:
			m = self.queue.get(block=True)
			if m["source"] == "module":
				self.agents[m["context"]["agent"]].receive(m)
			elif m["source"] == "agent":
				for a in self.modules:
					a.receive(m)

	def receive(self, msg):
		self.queue.put(msg)
