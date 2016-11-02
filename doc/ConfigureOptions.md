
It is common for modules and agents to have various options that they want their
users to set in the config.json, but users, being inheritly lazy, do not want to
actually edit a file, so it is nice if they have friendly prompts they can
answer when adding a module or agent to a local Halibot instance.

This interface enables the object implementer to configure his configuration.

The Configure class
===================

The `add` command will automatically create a class named `Configurer` that exists
on the module or agent class and call the `configure` function on that class. As
long as that class sets up the `config` field of the `Configurer` instance by
the end of the `configure` function, everything will work hunky dory, but in
order to make things easier, Halibot provides a class called `HalConfigurer`,
which you should definitely subclass.

The `HalConfigurer` class provides a method called `option` which prompts the
user to configure an option. For syntax is as follows:

```python
HalConfigurer.option(option_type, key=, prompt=, default=)
```

* `option_type` is an instance of a subclass of `Halibot.Option` that determines
  how to validate and prompt for the option.
* `key` is the name of the key in the config to set. If this is not set, the
  config object is returned from the function and it is the user's
  responsibility to set the appropriate field in `self.config`. Not setting this
  is useful for configuring things such as entries of an array within the config.
* `prompt` is the string to prompt the user with. If this is left blank, the
  `key` is used. If the `key` is also not set, an error is thrown.
* `default` a default value to use if the option is left blank. If no default
  value is given the key in the config is left unset.

Halibot further provides built-in subclasses of `Halibot.Option` for ease of
use. They are as follows:

* `Halibot.Option.String` for specifying an string option.
* `Halibot.Option.Int` for specifying an integer option.
* `Halibot.Option.Number` for specifying an real-valued number option.
* `Halibot.Option.Bool` for specifying an boolean option.

These option types are further made easily available via wrapper functions that
simply wrap to the underlying `HalConfigurer.option`, and are respectively as
follows:

* `HalConfigurer.optionString(key=, prompt=, default=)`
* `HalConfigurer.optionInt(key=, prompt=, default=)`
* `HalConfigurer.optionNumber(key=, prompt=, default=)`
* `HalConfigurer.optionBool(key=, prompt=, default=)`

The `HalConfigurer` class also has a `validate` function, which consumes the
user-defined configure function automatically and returns True or False
depending on whether or not the currently specified config is valid. The
validate function takes the optional parameter of `config` which will set the
config to check, where otherwise it checks the config already associated with
the configurer.

Example module with Configurer
------------------------------

```python
import time
from halibot import HalModule, HalConfigurer

class Responder(HalModule):

	class Configurer(HalConfigurer):
		def configure(self):
			self.optionString(key='accept', prompt='Accept string')
			self.optionString(key='return', prompt='Return string')
			self.optionInt(key='delay', prompt='Wait seconds before responding', default=0)

	def message(self, msg):
		if 'accept' in self.config and msg.body == self.config['accept']:
			time.sleep(self.config.get('delay', 0))
			self.reply(msg, body=self.config['return'])
```

The Option class
================

The `Option` class allows you to write your own prompting or validation
mechanisms for a specific object type.

There are four methods one should define:

* `configure(self, prompt)` which prompts the user for the value for this option
  type with the given prompt. Sets a `self.value` to the result of the prompt by
  default, calls `self.validate` to check, and reprompts if the validation failed.
* `validate(self)` which returns true if the option's value is valid. Always
  returns true by default.
* `get(self)` which retrieves the JSON-compliant value set for this option.
  Returns `self.value` by default.
* `set(self, value)` which sets a value for this option from the JSON-compliant
  value. Simply sets `self.value` by default.

Example custom Option class
---------------------------

```python
import halibot

class OptAlphanumeric(halibot.Option.String):
	def validate(self):
		return self.value.isalpha()

class OptEvenInt(halibot.Option.Int):
	def validate(self):
		return self.value % 2 == 0

import os
from tkinter.filedialog import askopenfilename

class OptFile(halibot.Option.String):
	def prompt(self):
		self.value = askopenfilename()

	def validate(self):
		os.path.exists(self.value)
```
