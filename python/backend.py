import soaculib

class _Backend:
    """Backend interface.  Abstract Base Class."""
    def __init__(self):
        self.decorator = None
        self.api_decorator = None
        self.return_val_func = None

    def execute(self, req):
        raise ValueError("Unimplemented request type '%s'" % req.req_type)
        yield None

    def __call__(self, *args, **kw):
        return self.execute(*args, **kw)


def get_backend(backend=None, persistent=None):
    if isinstance(backend, _Backend):
        return backend
    if backend is None or backend == 'standard':
        return soaculib.StandardBackend(persistent=persistent)
    if backend == 'twisted':
        from soaculib.twisted_backend import TwistedHttpBackend
        return TwistedHttpBackend(persistent=persistent)
    if backend == 'debug':
        return soaculib.DebuggingBackend()
    raise ValueError("Unknown backend request: %s" % backend)
