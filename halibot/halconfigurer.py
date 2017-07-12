
class Option():
	def __init__(self, key, prompt=None, default=None):
		self.key = key
		self.prompt = prompt if prompt != None else key
		self.default = default

	def ask(self):
		prompt = self.prompt
		if self.default != None:
			prompt += ' [' + str(self.default) + ']'
		prompt += ': '

		v = input(prompt)
		if v == '': return self.default
		return v

	def configure(self):
		while True:
			try:
				v = self.ask()
			except ValueError:
				continue
			if self.valid():
				break
		return v

	def valid(self):
		return True

# Builtin option classes
class StringOption(Option):
	pass

class IntOption(Option):
	def ask(self):
		return int(super().ask())

class NumberOption(Option):
	def ask(self):
		return float(super().ask())

class BooleanOption(Option):
	def ask(self):
		v = super().ask()
		if isinstance(v, str):
			if v.lower() == 'true':  return True
			if v.lower() == 'false': return False
			raise ValueError()
		return v

Option.String = StringOption
Option.Int = IntOption
Option.Number = NumberOption
Option.Boolean = BooleanOption

class HalConfigurer():

	def __init__(self):
		self.options = {}

	def option(self, option_type, key, **kwargs):
		opt = option_type(key, **kwargs)
		val = opt.configure()
		if val != None:
			self.options[key] = val

	def optionString(self, key, **kwargs):
		self.option(Option.String, key, **kwargs)

	def optionInt(self, key, **kwargs):
		self.option(Option.Int, key, **kwargs)

	def optionNumber(self, key, **kwargs):
		self.option(Option.Number, key, **kwargs)

	def optionBoolean(self, key, **kwargs):
		self.option(Option.Boolean, key, **kwargs)

	def configure(self):
		pass

