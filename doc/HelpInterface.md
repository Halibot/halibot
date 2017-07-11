# Halibot Help Text Interface

Help text is crucial for new users to learn how to operate modules and Halibot itself.
While Halibot core does not require module developers to supply help text, it is greatly encouraged to do so.
This document will define the help text ecosystem that is strongly recommended to adhere to.

# Sample Usage

## How to get help text?

### Via an agent (or "By chatting with it")

Halibot will provide a "Help" module as a default that needs to be enabled.
This handles the "!help" command, which has the following usage:

```
someuser> !help
halibot1> Your friendly bot! Use !help <module> to get specific module help
halibot1> Loaded modules: admin, help, quote

someuser> !help quote
halibot1> Display quotes from a file. Available commands are !quote, !quoteadd, !quotedel

someuser> !help quote !quoteadd
halibot1> Add a new quote to the db
halibot1> Call like so: !quoteadd text of new quote here

```

### Via command line

*do we actually want to support this?*

## How to implement help text?

```python
class Quote(HalModule):
    ...
    def help(args=None):
        if args == "!quoteadd":
              return "Add a new quote to the db\nCall like so: !quoteadd text of new quote here"
        return "Display quotes from a file. Available commands are !quote, !quoteadd, !quotedel"
```

That's it!
Nothing else needs to be done to support text through the !help interface.


# Specification

## Help Module

The Help module is fairly simple at its core.
It handles commands of the form `!help [module] [module topic]`

If nothing is supplied, it responds with a generic greeting, instructing the user to call again with `!help [module]` to learn more about specific modules.
It also should return a list of the currently loaded modules (which should also be available via the `admin` module's `!modules` command).

When only `module` is supplied (e.g. `!help quote`), the help module attempts to call the `help()` method on the selected module.
So in the example of the `quote` module, `!help quote` will find the module named `quote`, and call `.help()` on it via the `.invoke()` feature (see ModuleInteractivity.md for more on `.invoke()`).
If the specified module does not implement a `.help()` method, an apologetic error message is return instead.

If there are more than two words (separated by spaces) supplied to `!help`, the first word is considered to be module to inquire about, and everything after that space is considered supplementary text to query the module.
This supplementary text is passed into the module's `.help()` method, where it may or may not decide to respond differently.
Again, using the above example, `!help quote !quoteadd` invokes `quote`'s `.help()` method with the argument `"!quoteadd"`.
See the next section for recommendations on handling help topics.

## The `.help()` method

Help text on a module at its core, is just a function named `help` that returns a string.
All arguments to `.help()` should be treated as a string, and `.help()` should ONLY return a string.
Arguments may be omitted (as in, nonexistant, not just passing `None` or `""`), and thus the method should be able to handle either case.
Arguments do not need to be handled; the help method may choose to ignore any arguments.
Returned help text does not need to be deterministic, help methods may choose to modify the text based on the current running state.

## Tips for implementing a `.help()`.

### Output Formatting

As a general rule, try to avoid help text longer than three lines.
Most users will likely be coming from some kind of chat protocol like IRC or XMPP, therefore long messages could trigger a server rate limit.

### Command Modules

Modules that utilize a `!command` should probably list the available commands.
If using a dictionary to map command strings to functions, the keys of that dictionary can be conveniently used as a list.

Command modules should probably support both prefixed (`!command`) and non-prefixed (`command`) topics, for ease of use.

