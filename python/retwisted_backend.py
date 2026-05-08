"""Backend support for twisted, but using requests (called from
thread) instead of twisted.web.

"""
import soaculib

from twisted.internet import reactor, threads
from twisted.internet.defer import (
    inlineCallbacks, Deferred, returnValue)

import queue
import requests
import threading


class RetwistedHttpBackend(soaculib._Backend):
    """This backend returns a Deferred object from the execute() call.
    The final result will be decoded as usual.

    This differs from TwistedHttpBackend in that it uses requests
    library, under the hood, and this seems to be faster in some
    situations.  This implementation (in contrast to _NonPersistent)
    launches its own worker thread, instead of relying on Twisted
    threadpool, and thus can properly protect a single persistent
    requests session.  So it supports persistent connection, and
    that's the default.

    """

    def __init__(self, web_agent=None, persistent=True):
        """Calls requests.get/post, but wrapped in a Deferred.

        The http requests are issued in a thread, and thus persistent
        mode can be supported.

        """
        self.decorator = inlineCallbacks
        self.api_decorator = inlineCallbacks
        self.return_val_func = returnValue

        if persistent:
            self.session = requests.Session()
        else:
            self.session = requests

        self._get_args = {'timeout': 10.}
        self._post_args = {'timeout': 10.}

        self._q = queue.Queue()
        self._thread = threading.Thread(target=self._http_session_thread)

        if reactor.running:
            self._thread.start()
        else:
            reactor.callLater(0, self._thread.start)

    def _process_req(self, req):
        """Fully process a req -- make the get/post request, and
        decode the result. Encapsulates the call and decode that all
        exception handling is up to the caller.

        """
        if req.req_type == 'GET':
            t = self.session.get(req.url, params=req.params, **self._get_args)
        elif req.req_type == 'POST':
            t = self.session.post(req.url, params=req.params, data=req.data, **self._post_args)
        else:
            raise ValueError("Unimplemented request type '%s'" % req.req_type)

        # Decode the result.  To imitate TwistedHttpBackend,
        # convert response from str to bytes.
        result = req.decoder(t.status_code, bytes(t.text, 'utf8'))
        return result

    def _http_session_thread(self):
        while reactor.running:
            try:
                req, d = self._q.get(timeout=1.)
            except queue.Empty:
                continue

            try:
                decoded_result = self._process_req(req)

            except Exception as e:
                reactor.callFromThread(d.errback, e)
                continue

            reactor.callFromThread(d.callback, decoded_result)

    def execute(self, req):
        if not self._thread.is_alive():
            raise RuntimeError('RetwistedHttpBackend worker thread has died.')
        d = Deferred()
        self._q.put((req, d))
        return d

    def __call__(self, *args, **kw):
        return self.execute(*args, **kw)

    @inlineCallbacks
    def sleep(self, delay):
        d = Deferred()
        reactor.callLater(delay, d.callback, None)
        yield d


class RetwistedHttpBackend_NonPersistent(soaculib._Backend):
    """This backend returns a Deferred object from the execute() call.
    The final result will be decoded as usual.

    This differs from TwistedHttpBackend in that it uses requests
    library, under the hood, and this seems to be faster in some
    situations.

    This was the original implementation of RetwistedHttpBackend; it
    remains here temporarily to debug trouble with the new version.

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
        self._get_args = {'timeout': 10.}
        self._post_args = {'timeout': 10.}

        assert not persistent, "persistent=True not supported."

    def execute(self, req):
        def _request(req):
            if req.req_type == 'GET':
                t = self.session.get(req.url, params=req.params, **self._get_args)
            elif req.req_type == 'POST':
                t = self.session.post(req.url, params=req.params, data=req.data, **self._post_args)
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
