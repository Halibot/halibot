import logging
import asyncio
from threading import Thread
from .message import Message

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

	# See halmodule and halagent for their respective implementations
	def send(self, msg):
		pass

	def send_to(self, msg, dests):
		for name in dests:
			to = self._hal.get_object(name)
			if to:
				to._queue_msg(msg)
			else:
				self.log.warning('Unknown module/agent: ' + str(name))

	def reply(self, to, **kwargs):
		# TODO should we do something with misc?

		body = kwargs.get('body', None)
		author = kwargs.get('author', None) # TODO different default author?
		self.send(Message(body=body, context=to.context, author=author))

	def receive(self, msg):
		self.log.debug("Received from base: " + str(msg))
		pass

	def connect(self, to):
		# FIXME Don't modify the config like this?
		if 'out' in self.config:
			self.config['out'].append(to.name)
		else:
			self.config['out'] = [ to.name ]

