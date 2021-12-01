"""Backend support for twisted asynchronous framework.

"""
import soaculib

from twisted.internet import reactor
from twisted.internet.defer import (
    inlineCallbacks, Deferred, DeferredList, DeferredLock, returnValue)
import twisted.web.client as tclient
from twisted.web.http_headers import Headers

import urllib.parse
from io import BytesIO
import json

class TwistedHttpBackend(soaculib._Backend):
    """This backend returns a Deferred object from the execute() call.
    The final result will be decoded as usual.

    """

    def __init__(self, web_agent=None, persistent=False):
        """Instances of this class will make use of a twisted.web.client.Agent
        instance to perform web requests asynchronously.

        """
        self.decorator = inlineCallbacks
        self.api_decorator = inlineCallbacks
        self.return_val_func = returnValue

        if web_agent is None:
            if persistent is True:  # convert true to the classic default...
                persistent = 'pool2'
            if persistent == 'single':
                pool = SinglePersistentConnection(reactor)
                web_agent = tclient.Agent(reactor, pool=pool)
            elif persistent == 'pool1':
                pool = tclient.HTTPConnectionPool(reactor)
                pool.maxPersistentPerHost = 1
                web_agent = tclient.Agent(reactor, pool=pool)
            elif persistent == 'pool2':
                pool = tclient.HTTPConnectionPool(reactor)
                pool.maxPersistentPerHost = 2
                web_agent = tclient.Agent(reactor, pool=pool)
            else:
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

    @inlineCallbacks
    def sleep(self, delay):
        d = Deferred()
        reactor.callLater(delay, d.callback, None)
        yield d


class SinglePersistentConnection:
    """This "pool" is based on twisted.client.HTTPConnectionPool, and is
    supposed to stand in for it.  Instead of managing multiple
    connections, this enforces that a single connection be used for
    all communication with the server.

    """

    _factory = tclient._HTTP11ClientFactory

    def __init__(self, reactor):
        self.persistent = True
        self._locks = {}
        self._connections = {}

    def getConnection(self, key, endpoint):
        if key in self._locks:
            return self._locks[key].acquire().addCallback(
                lambda lock: self._connections[key])
        self._locks[key] = DeferredLock()
        def quiescentCallback(protocol):
            self._locks[key].release()
        factory = self._factory(quiescentCallback, repr(endpoint))
        cd = endpoint.connect(factory)
        def just_the_prot(results):
            ok, connection = results[0]
            if ok:
                self._connections[key] = connection
                return connection
            else:
                del self._locks[key]
                e.subFailure.raiseException()
        return DeferredList([cd, self._locks[key].acquire()]).addCallback(just_the_prot)

    def closeCachedConnections(self):
        """
        Close all persistent connections.

        @return: L{defer.Deferred} that fires when all connections have been
            closed.
        """
        results = []
        self._locks = {}
        for key, conn in self._connections.items():
            results.append(conn.abort())
        self._connections = {}
        return defer.gatherResults(results).addCallback(lambda ign: None)
