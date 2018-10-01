#!/usr/bin/env python3

import halibot
import json
import logging
import sys
import os
import shutil
import argparse
import code

DEFAULT_CONFIG = {
	"package-path": [
		"packages",
		os.path.join(os.path.abspath(os.path.dirname(__file__)), "packages")
	],
	"repos": ["https://halibot.fish:4842"],
	"agent-instances": {},
	"module-instances": {},
	"cli-instances": {
		"pm": {
			"of": "core:PackageManager"
		}
	}
}

def h_init(args):
	confpath = os.path.join(args.path, "config.json")
	pkgpath  = os.path.join(args.path, "packages")
	permpath = os.path.join(args.path, "permissions.json")

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

	with open(confpath, "w") as f:
		f.write(json.dumps(DEFAULT_CONFIG, sort_keys=True, indent=4))

	if not os.path.exists(permpath):
		with open(permpath, "w") as f:
			f.write(json.dumps([], sort_keys=True, indent=4))

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

	bot = halibot.Halibot()
	bot._load_config()

	logfile = None
	loglevel = logging.DEBUG
	loglevel_str = "DEBUG"
	loglevels = {
		"CRITICAL": logging.CRITICAL,
		"ERROR": logging.ERROR,
		"WARNING": logging.WARNING,
		"INFO": logging.INFO,
		"DEBUG": logging.DEBUG,
		"NOTSET": logging.NOTSET
	}

	# Set log level if argument is provided
	if args.log_level:
		loglevel_str = args.log_level
	elif "log-level" in bot.config:
		loglevel_str = bot.config["log-level"]

	# Error check log level string
	if loglevel_str not in loglevels:
		print("Log level '{}' invalid.".format(loglevel_str))
		return
	else:
		loglevel = loglevels[loglevel_str]

	# Set log file if argument is provided
	if args.log_file:
		logfile = args.log_file
	elif "log-file" in bot.config:
		logfile = bot.config["log-file"]

	logging.basicConfig(filename=logfile, level=loglevel)

	# Print used configuration
	if logfile:
		print("Logs at '{}' with log level '{}'".format(logfile, loglevel_str))
	else:
		print("Log level '{}'".format(loglevel_str))

	bot.start(block=True)

	if args.interactive:
		local = {
			"bot": bot,
			"halibot": halibot,
		}
		code.interact(banner="Halibot welcomes you!", local=local)
		bot.shutdown()
		print("Halibot bides you farewell.")


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

	bot._write_config()

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

	bot._write_config()

def h_config(args):
	# In order to access the config easily
	bot = halibot.Halibot()
	bot._load_config()

	if args.name in bot.config["agent-instances"]:
		destkey = "agent-instances"
	elif args.name in bot.config["module-instances"]:
		destkey = "module-instances"
	else:
		print('No such module or agent exists.')
		return
	pkgconf = bot.config[destkey][args.name]

	# Show or edit the config?
	if args.show:
		# Only a single key?
		if args.key != None:
			print(pkgconf[args.key])
		else:
			for k in pkgconf:
				print(k, "=", pkgconf[k])
	else:
		# Reconfigure the package
		if args.key != None:
			if args.value == None:
				print("You must specify a value with -v.")
				return

			# Detect the type to set
			if args.type:
				ty = args.type
			else:
				if args.key in pkgconf:
					typecls = type(pkgconf[args.key])
					if   typecls == int:   ty = "number"
					elif typecls == float: ty = "number"
					elif typecls == str:   ty = "string"
					elif typecls == bool:  ty = "boolean"
					else:
						print("The type of the key '" + args.key + "' is not a settable type.")
						return
				else:
					print("That key does not exist, you must specify the type with -t.")

			# Get the value
			if ty == "string": value = args.value
			if ty == "number": value = float(args.value)
			if ty == "boolean":
				if   args.value.lower() == 'true': value = True
				elif args.value.lower() == 'false': value = False
				else:
					print("Invalid boolean value, specify 'true' or 'false'.")
					return

			pkgconf[args.key] = value
		else:
			if not "of" in pkgconf:
				print("Corrupt config, package has no 'of' key.")
				return

			split = pkgconf["of"].split(":")
			if len(split) != 2:
				print("Corrupt config, malformed 'of' value.");
				return

			pkg = bot.get_package(split[0])
			if pkg == None:
				print("The package '" + split[0] + "' does not exist so it cannot be configured.")
				return

			cls = getattr(pkg, split[1], None)
			if not cls:
				print("The package '" + split[0] + "' has no module or agent named '" + split[1] + "'.")
				return


			(name, conf) = cls.configure(pkgconf, name=args.name)
			bot.config[destkey][name] = conf

		bot._write_config()

if __name__ == "__main__":
	subcmds = {
		"init": h_init,
		"run": h_run,
		"add": h_add,
		"rm": h_rm,
		"config": h_config,
	}

	# Setup argument parsing
	parser = argparse.ArgumentParser(description="The world's greatest saltwater chat bot!")

	sub = parser.add_subparsers(title="commands", dest="cmd", metavar="COMMAND")

	init = sub.add_parser("init", help="initialize a new local halibot instance")
	init.add_argument("path", help="directory path to initialize the halibot instance in", nargs="?", default=".")

	run = sub.add_parser("run", help="run the local halibot instance")
	run.add_argument("-i", "--interactive", help="enter a python shell after starting halibot", action="store_true", required=False)
	run.add_argument("-f", "--log-file", help="file to output logs to, none by default")
	run.add_argument("-l", "--log-level", help="level of logs, DEBUG by default")

	add = sub.add_parser("add", help="add agents or modules to the local halibot instance")
	add.add_argument("things", help="path to class to add", nargs="+", metavar="class")
	addtype = add.add_mutually_exclusive_group()
	addtype.add_argument("-a", "--agent", dest="destkey", action="store_const", const="agent-instances", help="add instances as agents")
	addtype.add_argument("-m", "--module", dest="destkey", action="store_const", const="module-instances", help="add instances as modules")

	rm = sub.add_parser("rm", help="remove agents or modules from the local halibot instance")
	rm.add_argument("names", help="names of agents or modules to remove", nargs="+", metavar="name")

	config_cmd = sub.add_parser("config", help="configure or reconfigure a module or agent")
	config_cmd.add_argument("name", help="name of the module or agent to show or reconfigure")
	config_cmd.add_argument("-s", "--show", action="store_true", help="show the configuration rather than set it", required=False)
	config_cmd.add_argument("-k", "--key", help="key to set or key to display with -s", required=False)
	config_cmd.add_argument("-v", "--value", help="value to set key to", required=False)
	config_cmd.add_argument("-t", "--type", choices=["string", "number", "boolean"], help="the type used while setting a config value with -k. If not given, it uses the type of the existing value")

	hal = halibot.Halibot(config=DEFAULT_CONFIG)
	try:
		hal._load_config("config.json")
	except Exception as e:
		pass

	if "cli-instances" in hal.config.keys():
		hal._instantiate_objects("cli")
		for o in hal.objects.values():
			o.cli(sub)

	args = parser.parse_args()

	# Try to run a subcommand
	func = subcmds.get(args.cmd)
	if func:
		func(args)
	else:
		for i in hal.objects.values():
			if i.cli_receive(args):
				break
		else:
			parser.print_help()

	hal.shutdown()
