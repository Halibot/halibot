import json
import logging
import re
from halibot.message import Message, MalformedMsgException

def hasPermission(perm, reply=False, argnum=None, key="msg", permissive=True):
	def real_dec(func):
		def wrapper(self, *args, **kwargs):
			if argnum != None and argnum < len(args):
				msg = args[argnum]
			else:
				msg = kwargs[key]

			# Origin must be set for this to be a valid permission check
			if not hasattr(msg, "origin") or not msg.origin:
				self.log.error("Probable module bug! -- hasPermission decorator called on a function that doesn't have a valid Message argument!")
				raise MalformedMsgException("Bad or missing origin attribute")
			# Identity may not be supported by agent, so we'll allow this to be blank
			if not hasattr(msg, "identity"):
				self.log.error("Probable module bug! -- hasPermission decorator called on a function that doesn't have a valid Message argument!")
				raise MalformedMsgException("Missing identity attribute")

			if self._hal.auth.hasPermission(msg.origin, msg.identity, perm, permissive):
				func(self, *args, **kwargs)
			elif reply:
				self.reply(msg, body="Permission Denied")
		return wrapper
	return real_dec

class HalAuth():

	def __init__(self):
		self.perms = []
		self.enabled = False
		self.log = logging.getLogger("Auth")

	# Load permission file, and set to enabled
	def load_perms(self, path):
		self.path = path

		try:
			with open(self.path, "r") as f:
				temp = json.loads(f.read())

			# Roll back into triple, also technically validates format
			self.perms = [(a,b,c) for a,b,c in temp]

		except Exception as e:
			self.log.error("Error loading permissions: {}".format(e))
			self.perms = []
			# Return if can't find auth?

		self.enabled = True

	# Write permissions back to the file that was originally loaded
	def write_perms(self):
		try:
			temp = [list(l) for l in self.perms]

			with open(self.path, "w") as f:
				f.write(json.dumps(temp, indent=4))
		except Exception as e: # pragma: no cover
				self.log.error("Error storing permissions: {}".format(e))

	def grantPermission(self, ri, identity, perm):
		if not self.enabled:
			return

		t = (ri, identity, perm)
		if t not in self.perms:
			self.perms.append(t)

	def revokePermission(self, ri, identity, perm):
		if not self.enabled:
			return

		try:
			self.perms.remove((ri,identity, perm))
		except Exception as e:
			self.log.error("Revocation failed: {}".format(e))

	def hasPermission(self, ri, identity, perm, permissive=True):
		if not self.enabled:
			return permissive

		def tester(x):
			a,b,c = x
			return re.match(a, ri) and b in (identity, "*") and re.match(c, perm)

		# Return True on the first successful perm match
		for l in self.perms:
			if tester(l):
				return True
		return False
