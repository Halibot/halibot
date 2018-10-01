import urllib.request
import tarfile
import io
import os
import argparse
import json
from halibot import HalModule

class PackageManager(HalModule):

	VERSION = "0.3.0"
	HAL_MINIMUM = "0.2.0"

	def init(self):
		self.commands = {
			"fetch":    self.h_fetch,
			"unfetch":  self.h_unfetch,
			"search":   self.h_search,
			"packages": self.h_list_packages
		}

		self.parser = argparse.ArgumentParser(description="PackageManager")
		self.cli(self.parser.add_subparsers(title="Package Management"))

	def receive(self, msg):
		if not msg.body.startswith("!"):
			return

		ls = msg.body[1:].split(" ")
		args = self.parser.parse_args(ls)

		func = self.commands.get(args.cmd)
		if not func:
			self.reply(msg, body="Command '{}' not found".format(args.cmd))
			return

		func(args, output=lambda x: output(x))

	def cli_receive(self, args):
		func = self.commands.get(args.cmd)
		if not func:
			return False

		func(args, output=print)
		return True

	# Expose the CLI argument logic
	def cli(self, parser):
		fetch = parser.add_parser("fetch", help="fetch remote packages")
		fetch.add_argument("packages", help="name of package to fetch", nargs="+", metavar="package")

		unfetch = parser.add_parser("unfetch", help="as if you never fetched them at all")
		unfetch.add_argument("packages", help="name of package to unfetch", nargs="+", metavar="package")

		search = parser.add_parser("search", help="search for packages")
		search.add_argument("term", help="what to search for", nargs="?", metavar="term")

		list_packages = parser.add_parser("packages", help="list all installed packages")


	def h_fetch(self, args, output):
		# In order to access the config easily
		bot = self._hal

		# Error checking
		if not "repos" in bot.config:
			output("There are no repos specified in the config.json.")
			output("I have nothing to fetch from!")
			return

		# Try to fetch each requested package
		for name in args.packages:
			# Install to the first package path by default
			dst = os.path.join(bot.config["package-path"][0], name)

			success = False
			for r in bot.config["repos"]:
				src = r + "/fetch/" + name
				try:
					output("Trying to fetch package from '{}'...".format(r))
					bio = io.BytesIO(urllib.request.urlopen(src).read())
					tar = tarfile.open(mode="r:*", fileobj=bio)
					os.mkdir(dst)
					tar.extractall(dst)

					output("\033[92mSuccessfully fetched '{}' into '{}'.\033[0m".format(name, dst))
					success = True
					break
				except Exception as e:
					output("Exception in pm: {}".format(e))

			if not success:
				output("\033[91mFailed to fetch '{}'!\033[0m".format(name))

	def h_search(self, args, output):
		# In order to access the config easily
		bot = self._hal

		# Error checking
		if not "repos" in bot.config:
			print("There are no repos specified in the config.json.")
			print("I have nowhere to search!")
			return

		# Query all listed repositories
		results = {}
		for r in bot.config["repos"]:
			url = r + "/search/"
			if args.term != None:
				url += args.term

			data = urllib.request.urlopen(url).read().decode('utf-8')
			subres = json.loads(data)
			results = dict(list(subres.items()) + list(results.items()))

		# Output results
		sorted_keys = list(results.keys())
		sorted_keys.sort()
		for name in sorted_keys:
			print(name, "-", results[name]['description'])


	def h_unfetch(self, args, output):
		# In order to access the config easily
		bot = self._hal

		# Remove each requested package
		for name in args.packages:
			# Install to the first package path by default
			success = False
			for pkgpath in bot.config["package-path"]:
				path = os.path.join(pkgpath, name)
				if os.path.exists(path):
					shutil.rmtree(path)
					output("Removed '{}' installed to '{}'.".format(name, path))
					success = True

			if not success:
				output("Could not find package '{}'".format(name))


	def h_list_packages(self, args, output):
		bot = self._hal

		pkgs = []
		for path in bot.config.get("package-path"):
			pkgs = pkgs + os.listdir(path)
		pkgs.sort()

		output("Installed packages: " + ", ".join(pkgs))
