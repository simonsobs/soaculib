import json
from collections import OrderedDict


def ordered_json(text):
    return json.loads(text, object_pairs_hook=OrderedDict)


class HttpError(Exception):
    pass


class HttpDecoder:
    """This class should be instantiated to provide the correct error
    checking and decoding mechanisms for some HttpRequest.  After
    instantiation, it may be used as a callable to process the
    response code and body text from an HTTP GET or POST operation.
    E.g.::

      decoder = HttpDecoder('cmd')
      resp_code, body_text = 200, 'Nope, wrong.'
      return decoder(resp_code, body_text)


    Except where noted below, the response code must be 200 or an
    HttpError will be raised.  When an error is not raised, the
    returned value depends on the response_type.

    If response_type is "json", then the returned value is the decoded
    JSON object (probably a dict).

    If response type is "cmd", then the returned value is a boolean
    that will be true if the reponse body text is "OK, Command
    executed."

    Otherwise, the returned value is simply the HTTP response body
    text as a string.

    """
    def __init__(self, response_type):
        self.rtype = response_type

    def __call__(self, resp_code, text):
        # Is the response valid?
        if resp_code != 200:
            raise HttpError("HTTP response code %i" % resp_code)

        if self.rtype == 'json':
            return ordered_json(text)
        elif self.rtype == 'cmd':
            return text == 'OK, Command executed.'
        else:
            return text


class HttpRequest:
    """This class is a container for requests (such as GET or POST to
    specific URLs) that can be passed to specific backends.

    This is basically an abstraction layer so we can use standard
    python requests (synchronous) or twisted (asynchronous) backends
    with the same front-end high-level API for the ACU platform
    control.

    """
    def __init__(self, req_type=None, url=None, params=None,
                 data=None, decoder='unknown'):
        self.req_type = req_type
        self.url = url
        self.params = params
        self.data = data
        if isinstance(decoder, str):
            decoder = HttpDecoder(decoder)
        self.decoder = decoder

#    def __repr__(self):
#        return self.req_type, self.url, self.params, self.data is not None
