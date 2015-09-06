from agent import Agent
import pydle, threading

class IrcAgent(Agent):
	
	client = None

	def init(self):
		self.client = IrcClient(nickname="halibot")
		self.client.agent = self
		self.client.connect(hostname="irc.freenode.net", port="6667",)
		self._start_client()


	def receive(self, msg):
		self.client.message(msg["context"]["whom"], msg["body"])

	def _start_client(self):
		self.thread = threading.Thread(target=self.client.handle_forever)
		self.thread.start()

class IrcClient(pydle.Client):

	agent = None

	def on_connect(self):
		super().on_connect()
		self.join(self.agent.config['channel'])

	def on_channel_message(self, target, by, text):
		msg = {}

		msg["body"] = text
		msg["type"] = "message"
		msg["author"] = by
		msg["context"] = {}
		msg["context"]["agent"] = self.agent.config["name"]
		msg["context"]["protocol"] = "irc"
		msg["context"]["whom"] = target

		self.agent.send(msg)

