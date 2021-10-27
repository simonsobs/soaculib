import soaculib

import requests
from functools import wraps
import types


class StandardBackend(soaculib._Backend):
    """HTTP backend that uses standard Python requests library."""
    def __init__(self, persistent=False):
        self.decorator = unyielding_decorator
        self.api_decorator = api_decorator
        self.return_val_func = returnValue
        self.session = requests
        if persistent:
            self.session = requests.Session()

    def execute(self, req):
        if req.req_type == 'GET':
            t = self.session.get(req.url, params=req.params)
        elif req.req_type == 'POST':
            t = self.session.post(req.url, params=req.params, data=req.data)
        else:
            raise ValueError("Unimplemented request type '%s'" % req.req_type)
        # Pass the result to the decoder.
        yield req.decoder(t.status_code, t.text)

    def __call__(self, *args, **kw):
        return self.execute(*args, **kw)


class DebuggingBackend:
    def __call__(self, req):
        return req


# The exception and function decorators below are used for wrapping
# generator-based code so it can be used more like a set of standard
# Python functions.


class _ReturnValue(BaseException):
    def __init__(self, value):
        self.value = value


def returnValue(x):
    raise _ReturnValue(x)


def unyielding_decorator(f):
    """Decorator analagous to Twisted's inlineCallbacks that turns a
    generator function that yields multiple values into a generator
    function that yields a single value.  All the other values yielded
    by the target generator are fed back in using send -- if those
    values happen to be generator functions, then the value is taken
    from the generator.

    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        gen = f(*args, **kwargs)
        val = None
        while True:
            try:
                # If the function has yielded a generator, it's the
                # first value from that gen that we want to extract.
                if isinstance(val, types.GeneratorType):
                    val = next(val)
                val = gen.send(val)
            except StopIteration:
                break
            except _ReturnValue as rv:
                val = rv.value
                break
        yield val
        raise StopIteration
    return wrapped


def api_decorator(f):
    """Like unyielding_decorator but produces a function (rather than
    another generator) that returns the ultimate value yielded by the
    target generator.

    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        gen = f(*args, **kwargs)
        val = None
        while True:
            try:
                # If the function has yielded a generator, it's the
                # first value from that gen that we want to extract.
                if isinstance(val, types.GeneratorType):
                    val = next(val)
                val = gen.send(val)
            except StopIteration:
                break
            except _ReturnValue as rv:
                val = rv.value
                break
        return val
    return wrapped
