"""Backend support for twisted, but using requests (called from
thread) instead of twisted.web.

"""
import soaculib

from twisted.internet import reactor, threads
from twisted.internet.defer import (
    inlineCallbacks, Deferred, returnValue)

import requests

import queue
import threading

def thread_str():
    pool = reactor.getThreadPool()
    return f'tpool size={len(pool.threads)},idle={len(pool.waiters)},pthreads={threading.active_count()}'

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
        self._get_args = {'timeout': 10.}
        self._post_args = {'timeout': 10.}

        assert not persistent, "persistent=True not supported."

    def execute(self, req):
        def _request(req):
            if req.req_type == 'GET':
                print(req.url, req.params, thread_str())
                t = self.session.get(req.url, params=req.params, **self._get_args)
                print('recd', len(t.text), thread_str())
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

class RetwistedHttpBackend2(soaculib._Backend):
    """This backend returns a Deferred object from the execute() call.
    The final result will be decoded as usual.

    This differs from TwistedHttpBackend in that it uses requests
    library, under the hood, and this seems to be faster in some
    situations.

    """

    def __init__(self, web_agent=None, persistent=False):
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
            print(req.url, req.params, 'rt2')
            t = self.session.get(req.url, params=req.params, **self._get_args)
            print('recd', len(t.text), 'rt2')
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
                print('Exception in get/post/decode:', e)
                reactor.callFromThread(d.errback, e)
                continue

            reactor.callFromThread(d.callback, decoded_result)

    def execute(self, req):
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
