"""Backend support for twisted asynchronous framework.

"""
import aculib

from twisted.internet import reactor
from twisted.internet.defer import (
    inlineCallbacks, Deferred, DeferredList, returnValue)
import twisted.web.client as tclient
from twisted.web.http_headers import Headers

import urllib.parse
from io import BytesIO
import json

class TwistedHttpBackend(aculib._Backend):
    """This backend returns a Deferred object from the execute() call.
    The final result will be decoded as usual.

    """

    def __init__(self, web_agent=None):
        """Instances of this class will make use of a twisted.web.client.Agent
        instance to perform web requests asynchronously.

        """
        self.decorator = inlineCallbacks
        self.api_decorator = inlineCallbacks
        self.return_val_func = returnValue

        if web_agent is None:
            web_agent = tclient.Agent(reactor)

        self.web_agent = web_agent

    def execute(self, req):
        # Form the url, including params.  Use quote() to turn ' '
        # into %20 and so on.
        url_params = '&'.join(['%s=%s' % (k, urllib.parse.quote(v))
                               for k,v in req.params.items()])
        full_url = ('%s?%s' % (req.url, url_params))
        if req.req_type == 'GET':
            defd = self.web_agent.request(
                b'GET', bytes(full_url, 'utf-8'))
        elif req.req_type == 'POST':
            headers = {}
            defd = self.web_agent.request(
                b'POST', bytes(full_url, 'utf-8'),
                Headers(headers),
                tclient.FileBodyProducer(BytesIO(bytes(req.data, 'utf-8'))))
        else:
            raise ValueError("Unimplemented request type '%s'" % req.req_type)
        
        # Attach the relevant handler as a callback.
        @inlineCallbacks
        def _decoder(result, decoder_func):
            status_code, text = result.code, ''
            if result.code == 200:
                text = yield tclient.readBody(result)
            return decoder_func(status_code, text)

        defd.addCallback(_decoder, req.decoder)
        return defd

    def __call__(self, *args, **kw):
        return self.execute(*args, **kw)
