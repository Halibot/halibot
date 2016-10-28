#!/usr/bin/env python3

import halibot
import json
import logging
import sys
import os
import shutil
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
	else:  # Dir does exist, ensure clear
		if os.listdir(args.path):
			r = input("Directory not empty, are you sure you want to init here? [y/N]: ")
			if not r.lower() in ("y", "yes", "yolo"):
				return

	if os.path.exists(confpath):
		r = input("A 'config.json' already exists, overwrite with new? [y/N]: ")
		if not r.lower() in ("y", "yes", "yolo"):
			return

	config = {
		"package-path": [
			"packages",
			os.path.join(os.path.abspath(os.path.dirname(__file__)), "packages")
		],
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
	print("\nUse '{} run' to run the instance, or edit 'config.json' to add module/agent instances".format(sys.argv[0]))

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

def h_unfetch(args):
	# In order to access the config easily
	bot = halibot.Halibot()
	bot._load_config()

	# Remove each requested package
	for name in args.packages:
		# Install to the first package path by default
		success = False
		for pkgpath in bot.config["package-path"]:
			path = os.path.join(pkgpath, name)
			if os.path.exists(path):
				shutil.rmtree(path)
				print("Removed '{}' installed to '{}'.".format(name, path))
				success = True

		if not success:
			print("Could not find package '{}'".format(name))


def h_list_packages(args):
	bot = halibot.Halibot()
	bot._load_config()

	pkgs = []
	for path in bot.config.get("package-path"):
		pkgs = pkgs + os.listdir(path)
	pkgs.sort()

	print("\nInstalled packages:")
	for p in pkgs:
		print("  {}".format(p))
	print("")

def h_add(args):
	# In order to access the config easily
	bot = halibot.Halibot()
	bot._load_config()

	for clspath in args.things:
		# Validate that it is actually an object
		split = clspath.split(":")
		if len(split) > 2:
			print("Invalid class path '{}', expected no more than 1 colon (:).".format(clspath))
			continue

		pkg = bot.get_package(split[0])
		if pkg == None:
			print("Cannot find package '{}'.".format(split[0]))
			continue

		if len(split) == 1:
			if not hasattr(pkg, "Default"):
				print("Package '{}' has no default class, must specify the class to add explicitly.".format(split[0]))
				continue
			cls = pkg.Default
			clspath += ":Default"
		else:
			cls = getattr(pkg, split[1], None)
			if cls == None:
				print("Class '{}' does not exist on package '{}'.".format(split[1], split[0]))
				continue

		if args.destkey:
			destkey = args.destkey
		else:
			if issubclass(cls, halibot.HalModule):
				destkey = "module-instances"
			elif issubclass(cls, halibot.HalAgent):
				destkey = "agent-instances"
			else:
				print("Cannot determine if '{}' is a module or agent, use '-m' or '-a'.")
				continue

		(name, conf) = cls.configure({ 'of': clspath })

		if name in bot.config["agent-instances"] or name in bot.config["module-instances"]:
			print("Instance name '{}' is already in configuration, please choose a different instance name".format(name))
			return

		bot.config[destkey][name] = conf

	with open("config.json","w") as f:
		f.write(json.dumps(bot.config, sort_keys=True, indent=4))

def h_rm(args):
	# In order to access the config easily
	bot = halibot.Halibot()
	bot._load_config()

	for name in args.names:
		if name in bot.config["agent-instances"]:
			bot.config["agent-instances"].pop(name)
		elif name in bot.config["module-instances"]:
			bot.config["module-instances"].pop(name)
		else:
			print("No such object '{}'".format(name))
			continue
		print("Removed '{}'.".format(name))

	with open("config.json", "w") as f:
		f.write(json.dumps(bot.config, sort_keys=True, indent=4))

if __name__ == "__main__":
	subcmds = {
		"init": h_init,
		"run": h_run,
		"fetch": h_fetch,
		"unfetch": h_unfetch,
		"add": h_add,
		"rm": h_rm,
		"packages": h_list_packages,
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

	unfetch = sub.add_parser("unfetch", help="as if you never fetched them at all")
	unfetch.add_argument("packages", help="name of package to unfetch", nargs="+", metavar="package")

	add = sub.add_parser("add", help="add agents or modules to the local halibot instance")
	add.add_argument("things", help="path to class to add", nargs="+", metavar="class")
	addtype = add.add_mutually_exclusive_group()
	addtype.add_argument("-a", "--agent", dest="destkey", action="store_const", const="agent-instances", help="add instances as agents")
	addtype.add_argument("-m", "--module", dest="destkey", action="store_const", const="module-instances", help="add instances as modules")

	rm = sub.add_parser("rm", help="remove agents or modules from the local halibot instance")
	rm.add_argument("names", help="names of agents or modules to remove", nargs="+", metavar="name")

	list_packages = sub.add_parser("packages", help="list all installed packages")

	args = parser.parse_args()

	# Try to run a subcommand
	if args.cmd != None:
		subcmds[args.cmd](args)
	else:
		parser.print_help()
