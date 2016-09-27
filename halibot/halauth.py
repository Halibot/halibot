import json
import logging

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
			# Return if can't find auth?

		self.enabled = True

	# Write permissions back to the file that was originally loaded
	def write_perms(self):
		try:
			temp = [list(l) for l in self.perms]

			with open(self.path, "w") as f:
				f.write(json.dumps(temp, indent=4))
		except Exception as e:
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

	def hasPermission(self, ri, identity, perm):
		if not self.enabled:
			return True

		def tester(x):
			a,b,c = x
			return a in (ri, "*") and b in (identity, "*") and c in (perm, "*")

		# Return True on the first successful perm match
		for l in self.perms:
			if tester(l):
				return True
		return False
