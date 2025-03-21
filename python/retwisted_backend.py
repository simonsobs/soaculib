"""Backend support for twisted, but using requests (called from
thread) instead of twisted.web.

"""
import soaculib

from twisted.internet import reactor, threads
from twisted.internet.defer import (
    inlineCallbacks, Deferred, returnValue)

import requests

class RetwistedHttpBackend(soaculib._Backend):
    """This backend returns a Deferred object from the execute() call.
    The final result will be decoded as usual.

    This differs from TwistedHttpBackend in that it uses requests
    library, under the hood, and this seems to be faster in some
    situations.

    """

    def __init__(self, web_agent=None, persistent=False):
        """Calls requests.get/post, but wrapped in a Deferred.

        The persistent mode is not supported here, as that would
        require queuing requests or otherwise worrying about
        thread-safety of requests.Session.

        """
        self.decorator = inlineCallbacks
        self.api_decorator = inlineCallbacks
        self.return_val_func = returnValue

        self.session = requests
        assert not persistent, "persistent=True not supported."

    def execute(self, req):
        def _request(req):
            if req.req_type == 'GET':
                t = self.session.get(req.url, params=req.params)
            elif req.req_type == 'POST':
                t = self.session.post(req.url, params=req.params, data=req.data)
            else:
                raise ValueError("Unimplemented request type '%s'" % req.req_type)
            # Decode the result.  To imitate TwistedHttpBackend,
            # convert response from str to bytes.
            return req.decoder(t.status_code, bytes(t.text, 'utf8'))

        return threads.deferToThread(_request, req)

    def __call__(self, *args, **kw):
        return self.execute(*args, **kw)

    @inlineCallbacks
    def sleep(self, delay):
        d = Deferred()
        reactor.callLater(delay, d.callback, None)
        yield d
