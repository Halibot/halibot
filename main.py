#!/usr/bin/env python3

import halibot
import json
import logging
import sys
import os
import zipfile
import tarfile
import urllib.request
import io
import argparse
import code

noGit = False
try:
	from git import Repo
except ImportError:
	noGit = True

def h_init(args):
	confpath = os.path.join(args.path, "config.json")
	pkgpath  = os.path.join(args.path, "packages")

	if not os.path.exists(args.path):
		os.mkdir(args.path)
	else: # Dir does exist, ensure clear
		if os.listdir(args.path):
			r = input("Directory not empty, are you sure you want to init here? [y/N]: ")
			if not r.lower() in ("y", "yes", "yolo"):
				return

	if os.path.exists(confpath):
		r = input("A 'config.json' already exists, overwrite with new? [y/N]: ")
		if not r.lower() in ("y", "yes", "yolo"):
			return

	config = {
		"package-path": ["packages"],
		"repos": ["git://github.com/halibot-extra/{}"],
		"agent-instances": {},
		"module-instances": {}
	}

	with open(confpath, "w") as f:
		f.write(json.dumps(config, sort_keys=True, indent=4))

	if not os.path.exists(pkgpath):
		os.mkdir(pkgpath)
		print("Created '{}'".format(pkgpath))

	print("Halibot instance has been initialized!")
	print("\nUse '{} run' to run the instance, or edit 'config.json' to add module/agent instances")

def h_run(args):
	# Maybe do the config loading here?
	if not os.path.exists("config.json"):
		print("Failed to start: No halibot configuration found in the current directory!")
		return

	logging.basicConfig(level=logging.DEBUG)
	bot = halibot.Halibot()
	bot.start(block=True)

	if args.interactive:
		local = {
			"bot": bot,
			"halibot": halibot,
		}
		code.interact(banner="Halibot welcomes you!", local=local)
		bot.shutdown()
		print("Halibot bides you farewell.")

def h_fetch(args):
	# In order to access the config easily
	bot = halibot.Halibot()
	bot._load_config()

	# Error checking
	if not "repos" in bot.config:
		print("There are no repos specified in the config.json.")
		print("I have nothing to fetch from!")
		return

	# Try to fetch each requested package
	for name in args.packages:
		# Install to the first package path by default
		dst = os.path.join(bot.config["package-path"][0], name)

		success = False
		for r in bot.config["repos"]:
			src = r.format(name)
			try:
				if src.startswith("git://"):
					if noGit:
						raise Exception("The git module is not installed, I cannot clone git repos.")
					print("Trying to git clone '{}'...".format(src))
					Repo.clone_from(src, dst)
				elif src.endswith(".zip"):
					print("Trying to extract zip from '{}'...".format(src))
					bio = io.BytesIO(urllib.request.urlopen(src).readall())
					z = zipfile.ZipFile(bio)
					os.mkdir(dst)
					z.extractall(dst)
				elif src.endswith( (".tar", ".tar.gz", ".tar.bz", ".tar.xz" ) ):
					print("Trying to extract tarball from '{}'...".format(src))
					bio = io.BytesIO(urllib.request.urlopen(src).readall())
					tar = tarfile.open(mode="r:*", fileobj=bio)
					os.mkdir(dst)
					tar.extractall(dst)
				else:
					raise Exception("I do not know how to handle the path '{}'".format(src))

				print("\033[92mSuccessfully fetched '{}' into '{}'.\033[0m".format(name, dst))
				success = True
				break
			except Exception as e:
				print(e)

		if not success:
			print("\033[91mFailed to fetch '{}'!\033[0m".format(name))

def h_add_agent(args):
	_h_add("agent-instances", args)

def h_add_module(args):
	_h_add("module-instances", args)

def _h_add(destkey, args):
	# In order to access the config easily
	bot = halibot.Halibot()
	bot._load_config()

	for clspath in args.things:
		# Validate that it is actually an object
		split = clspath.split(":")
		if len(split) != 2:
			print("Invalid class path '{}', expected exactly 1 colon (:).".format(clspath))
			continue

		pkg = bot.get_package(split[0])
		if pkg == None:
			print("Cannot find package '{}'.".format(split[0]))
			continue

		cls = getattr(pkg, split[1], None)
		if cls == None:
			print("Class '{}' does not exist on package '{}'.".format(split[1], split[0]))
			continue

		conf = { "of": clspath }
		name = input("Enter instance name: ")

		for key in getattr(cls, "options", {}):
			opt = cls.options[key]

			prompt = opt["prompt"]
			if "default" in opt:
				prompt += " [" + str(opt["default"]) + "]: "
			else:
				prompt += ": "

			val = input(prompt)
			if val == '':
				if "default" in opt:
					val = opt["default"]
				else:
					# Don't write this key
					continue

			if opt["type"] == "int":
				conf[key] = int(val)
			elif opt["type"] == "float":
				conf[key] = float(val)
			elif opt["type"] == "bool":
				conf[key] = (val.lower() == "true")
			else:
				conf[key] = val

		bot.config[destkey][name] = conf

	with open("config.json","w") as f:
		f.write(json.dumps(bot.config, sort_keys=True, indent=4))


if __name__ == "__main__":
	subcmds = {
		"init": h_init,
		"run": h_run,
		"fetch": h_fetch,
		"add-agent": h_add_agent,
		"add-module": h_add_module,
	}

	# Setup argument parsing
	parser = argparse.ArgumentParser(description="The world's greatest saltwater chat bot!")

	sub = parser.add_subparsers(title="commands", dest="cmd", metavar="COMMAND")

	init = sub.add_parser("init", help="initialize a new local halibot instance")
	init.add_argument("path", help="directory path to initialize the halibot instance in", nargs="?", default=".")

	run = sub.add_parser("run", help="run the local halibot instance")
	run.add_argument("-i", "--interactive", help="enter a python shell after starting halibot", action="store_true", required=False)

	fetch = sub.add_parser("fetch", help="fetch remote packages")
	fetch.add_argument("packages", help="name of package to fetch", nargs="+", metavar="package")

	add_agent = sub.add_parser("add-agent", help="add agents to the local halibot instance")
	add_agent.add_argument("things", help="agent class path to add", nargs="+", metavar="agent")

	add_module = sub.add_parser("add-module", help="add modules to the local halibot instance")
	add_module.add_argument("things", help="module class path to add", nargs="+", metavar="module")

	args = parser.parse_args()

	# Try to run a subcommand
	if args.cmd != None:
		subcmds[args.cmd](args)
	else:
		parser.print_help()
