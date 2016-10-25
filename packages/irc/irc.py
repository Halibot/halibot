# 
# Reference Halibot IRC Agent
#  Connects to an IRC server and relays messages to and from the base
#
from halibot import HalAgent, Context, Message
import pydle, threading

# Haliot Reference IRC Agent
#  Creates a Pydle IRC Client and connects to a server
#  Receives messages from the server, relays them to the Halibot base
#  Receives messages from the Halibot base, relays them to the IRC server
class IrcAgent(HalAgent):

	options = {
		'nickname': {
			'type'    : 'string',
			'prompt'  : 'Nickname',
			'default' : 'halibot',
		},
		'hostname': {
			'type'    : 'string',
			'prompt'  : 'Server hostname',
			'default' : 'irc.freenode.net',
		},
		'port': {
			'type'    : 'string',
			'prompt'  : 'Server port',
			'default' : '6667',
		},
		'channel': {
			'type'    : 'string',
			'prompt'  : 'Channel to join',
		},
	}

	# Handle to the Pydle IRC Client object as defined below
	client = None

	# Called when the IrcAgent is instantiated.
	#  Anything needed to get the agent running should go in here,
	#  NOT in __init__()!
	def init(self):
		# Create the IRC client object as defined/extended below
		self.client = IrcClient(nickname=self.config['nickname'])
		
		# Give the client object a handle to talk back to this agent class
		self.client.agent = self 
		
		self.client.connect(hostname=self.config['hostname'], port=self.config['port'])
		self._start_client()

	# Implement the receive() function as defined in the HalModule class
	#  This is called when the Halibot wants to send a message out using this agent.
	#  In this case, the logic for sending a message to the IRC channel is put here,
	#  using the whom as the "channel", which is the tail end of the resource
	#  identifier for this target (e.g. the "#foo" in "irc/#foo").
	def receive(self, msg):
		self.client.message(msg.whom(), msg.body)


	def shutdown(self):
		self.client.disconnect()
		self.client.eventloop.stop()
		self.thread.join()

	# Start the thread the IRC client will live in
	#  This is so the client does not block on halibot's instantiation (main) thread,
	#  thus causing to stop there and never finish starting up
	def _start_client(self):
		self.thread = threading.Thread(target=self.client.handle_forever)
		self.thread.start()
	
	# NOTE: The Module() base class implements a send() function, do NOT override this.
	#  The function is used to send to the Halibot base for module processing.
	#  Simply implementing the receive() function is enough to get messages from the modules,
	#   to get messages from your agent targer (IRC, XMPP, etc), that is up to the developer.



# Pydle IRC Client class.
#  This will handle all the IRC work, and talks to the base via the IRCAgent
#  The following is for reference, some of which will be pydle-specific
class IrcClient(pydle.Client):

	# Handle to the IRC Agent above
	agent = None

	# Pydle calls this when the client connects to the server.
	#  Sets the channel(s) to join from the agent's config.
	#  NOTE: the config field is automatically populated from the relevant
	#   config files when the module is loaded
	def on_connect(self):
		super().on_connect()
		# TODO: Allow joining of multiple channels
		self.join(self.agent.config['channel'])

	# Pydle calls this when a message is received from the server
	#  The purpose of this agent is to communicate with IRC,
	#  so this repackages the message from Pydle into a Halibot-friendly message
	def on_channel_message(self, target, by, text):
		org = self.agent.name + '/' + target
		msg = Message(body=text, author=by, origin=org)

		# Send the Halibot-friendly message to the Halibot base for module processing
		self.agent.dispatch(msg)
