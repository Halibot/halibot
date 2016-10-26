import logging
import asyncio
import inspect
import copy
from threading import Thread

class HalObject():

	def __init__(self, hal, conf={}):
		self._hal = hal
		self.config = conf
		self.log = logging.getLogger(self.__class__.__name__) # TODO: Put instantiated name in here too

		self.eventloop = asyncio.SelectorEventLoop()
		self._thread = Thread(target=self.eventloop.run_forever)
		self._thread.start()

	def _shutdown(self):
		self.eventloop.call_soon_threadsafe(self.eventloop.stop)
		self._thread.join()
		self.shutdown()

	def _queue_msg(self, msg):
		self.eventloop.call_soon_threadsafe(self.receive, msg)

	def init(self):
		pass

	def shutdown(self):
		pass

	def send_to(self, msg, dests):
		# Set origin for those who have not set it manually
		if msg.origin == None:
			msg.origin = self.name

		for ri in dests:
			name = ri.split('/')[0]
			to = self._hal.objects.get(name)
			if to:
				nmsg = copy.copy(msg)
				nmsg.target = ri
				to._queue_msg(nmsg)
			else:
				self.log.warning('Unknown module/agent: ' + str(name))

	def receive(self, msg):
		pass

	# Configures an instance of this class based on the 'options' attribute
	@classmethod
	def configure(cls, conf):
		name = input('Enter instance name: ')

		for key in getattr(cls, 'options', {}):
			opt = cls.options[key]

			prompt = opt['prompt']
			if 'default' in opt:
				prompt += ' [' + str(opt['default']) + ']: '
			else:
				prompt += ': '

			val = input(prompt)
			if val == '':
				if 'default' in opt:
					val = opt['default']
				else:
					# Don't write this key
					continue

			if opt['type'] == 'int':
				conf[key] = int(val)
			elif opt['type'] == 'float':
				conf[key] = float(val)
			elif opt['type'] == 'bool':
				conf[key] = (val.lower() == 'true')
			else:
				conf[key] = val

		return name, conf

	def invoke(self, inst, method, *args, **kwargs):
		return getattr(self._hal.objects[inst], method)(*args, **kwargs)
