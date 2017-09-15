#
# Hello World reference Halibot Module
#  Replies to any message starting with "!hello"
#
from halibot import HalModule, Message

# Hello Module
#  Upon receiving a message from any source, checks if the body of that message
#  starts with the literal string "!quote"
#  If so, responds with "Hello World!" via the same way the message was received
class Hello(HalModule):

	# Module version strings
	#  These should be defined so that Halibot can safety-check modules prior to
	#  loading that may use unimplemented or deprecated features
	#  VERSION - what is the version of this module (for reference), using semver.
	#  HAL_MINIMUM - minimum version of Halibot core that this module will work with
	#  HAL_MAXIMUM - (optional) reject Halibot core versions newer than this.

	VERSION = "1.0.0"
	HAL_MINIMUM = "0.1"

	# Called when the module is initialized
	#  Put any initialization logic here, instead of __init__()
	#  In this case, no initialization is needed, thus it is a no-op
	#  This is already defined in HalModule, so it can be excluded if not needed
	def init(self):
		pass

	# Called when a new message from the Halibot base is received
	#  The `msg` argument is in the standard Halibot message format, regardless of the actual source
	#  Thus, even it was from IRC, XMPP, etc, it should have keys like "body", for the actual text.
	#  To where it comes from, check the "context" field.
	def receive(self, msg):
		# The "body" field should always be populated, thus this is a safe assumption.(otherwise, an agent isn't working properly!
		if msg.body.startswith("!hello"):
			# Send a message back to the sender, using the same method that was used to receive it
			self.reply(msg, body="Hello world!")

	# NOTE: The HalModule also includes a send() method, which reply() calls out to
	#  reply() is the same as send()'ing a copy of the received message, with a new body
	#  Do NOT override send() or reply(), they are already implemented for you.
