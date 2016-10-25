# Module Interactivity

Modules are intentionally not closed off from one another so that they may share resources or provide services.
In many cases, it doesn't make sense to duplicate effort across various modules.
Thus, Halibot core provides an `invoke` method on all HalObjects that can be used to simplify the process.
This document will use calling a method on a module as an example, but the exact same interface can be used for calling a method from/on an agent.

# HalModule Invoke API Usage

## Overview

Module interactivity is dependent on two things:
 - Instance name of target module
 - Name of method to call

The instance name needs to be provided to ensure that the right module is used.
It is recommend to include the module instance name as a configuration option, so that it can be changed easily.
If the instance name is not found, then an `KeyError` exception will be thrown.

The method name must also be exactly as it appears in the module's source.
It is recommended to document all methods that are intended to be exposed for interactive use in the respective module's README.
If the method is not found on the target module's instantiation (object), then a `NameError` exception will be thrown.

## Examples

Consider the following example module.
This module will be used as the basis for the following examples, instantiated under the name "hello".

```python
class Hello(HalModule):

    # Regular method that only returns a string
    def sayHello(self):
        return "Hello!"

    # Method with one mandatory argument
    def sayHelloToUser(self, user):
        return "Hello {}!".format(user)

    # Method with an optional argument
    def sayHelloOrNot(self, user=""):
        return self.sayHelloToUser(user) if user else self.sayHello()

```

### Example \#1: No arguments

```python
class Respond(HalModule):

    def receive(self, msg):
        if msg.body == "!hello":
            resp = self.invoke("hello","sayHello")
            self.reply(msg, body=resp)
```

This calls the `sayHello()` method on the `Hello` module instantiated as `hello`.
Note there are no protections here, so if the `hello` module is either renamed or removed, an exception will be uncaught.
While Halibot can handle the uncaught exceptions, it is generally not a good idea to let those go.

This is a better version of the same implementation:

```python
class Respond(HalModule):

    def receive(self, msg):
        if msg.body == "!hello":
            try:
                resp = self.invoke("hello","sayHello")
            except NameError:
                resp = "Could not find .sayHello()"
            except KeyError:
                resp = "Cound not find 'hello' module"
            self.reply(msg, body=resp)
```
This is a bit more unwieldy, but this provides some useful feedback to debug the problem, and does not clutter the log with unhandled exceptions.

### Example \#2: Positional Arguments

The `.invoke()` method will relay positional arguments, so there are two forms that this can take:

```python
resp = self.invoke("hello","sayHelloToUser", msg.author)
# resp -> "Hello {author}!"


resp = self.invoke("hello","sayHelloToUser", *(msg.author))
# resp -> "Hello {author}!"
```

Arguments can be passed either as additional arguments to the `.invoke()` function, or as a tuple using the * operator.
Either are valid, and can be used to suit the use case.

### Example \#3: Optional Arguments

```python
resp = self.invoke("hello","sayHelloOrNot")
# resp -> "Hello!"


resp = self.invoke("hello","sayHelloOrNot", user=msg.author)
# resp -> "Hello {author}!"
```
