import soaculib

# As is the case for AcuControl, the public interface for
# BroadcastStreamControls will be created on instantiation by
# wrapping the private methods (implemented as generators) with a
# public name.  The public names should be listed in the variable
# INTERFACE, for automatic wrapping.  For public function
# ``do_something``, the private function should be called
# ``_do_something``.


class BroadcastStreamControl:
    """Control of the fast datasets provided over UDP, such as the Angular
    Measurement Dataset (PositionBroadcast).

    """
    INTERFACE = ['safe_enable', 'enable', 'get_status',
                 'set_destination', 'set_port', 'set_config']

    @classmethod
    def get_all(cls, config='guess', backend=None):
        """Returns handler objects for all streams in the specified config
        (use 'guess' to load the config based on hostname).

        """
        config = soaculib.guess_config(config)
        output = {}
        for name, stream_cfg in config.get('streams', {}).items():
            if not stream_cfg.get('active', True):
                continue
            output[name] = cls(config, stream_cfg, backend=None)
        return output

    def __init__(self, config, stream_config, backend=None):
        """Args:

            config: a system config spec (dict, system name, or
                'guess').
            stream_config: a stream config spec (dict, stream name).

        """
        # Decode configs.
        if isinstance(config, str):
            config = soaculib.guess_config(config)
        if isinstance(stream_config, str):
            stream_name = stream_config
            stream_config = config['streams'][stream_name]
        else:
            stream_name = stream_config.get('name', 'unknown')
        # Store key parameters locally.
        self.p = {
            # The "developer" http interface base URL.
            'dev_url': config['dev_url'],
            # The Module to access.
            'module': f'Services.{stream_config["acu_name"]}',
            # Target IP and port for UDP packets.
            'Destination': config['interface_ip'],
            'Port': str(stream_config['port']),
            # Schema
            'schema': stream_config.get('schema'),
        }
        # If config specifies schema by name, replace it with dict.
        if isinstance(self.p['schema'], str):
            self.p['schema'] = soaculib.get_stream_schema(self.p['schema'])

        backend = soaculib.get_backend(backend)
        self.http = ModularHttpInterface(
            self.p['dev_url'], backend=backend)

        # Decorate all methods for the chosen backend.
        for public_name in self.INTERFACE:
            func = getattr(self, '_' + public_name)
            setattr(self, '_' + public_name, backend.decorator(func))
            setattr(self, public_name, backend.api_decorator(func))
        # Define the appropriate returnValue function.
        self._return_val_func = backend.return_val_func

    def _return(self, value):
        self._return_val_func(value)

    def _safe_enable(self, force_reconfig=False):
        """Enable the stream, after checking the destination IP and port and
        updating them if need be.

        If reconfiguration is necessary (or if force_reconfig), then
        the stream will be disabled before being re-enabled.

        Returns the get_status() output, after enabling the stream.

        """
        if not force_reconfig:
            # Check the active settings and maybe force a reconfig.
            _, current_cfg = yield self.get_status()
            force_reconfig = (self.p['Port'] != int(current_cfg['Port'])) \
                or (self.p['Destination'] != current_cfg['Destination'])
        if force_reconfig:
            yield self.disable()
            yield self.set_config()
        yield self.enable()
        status, cfg = yield self.get_status()
        self._return((status, cfg))

    def _enable(self, enable=True):
        """Enable (or disable) the stream UDP output using the developer
        interface.

        Note this does not check or update the port and IP settings
        before enabling the stream; see safe_enable().

        """
        data = {'Command': {True: 'Enable', False: 'Disable'}[enable]}
        # At the present time, this system returns a huge web page
        # dump in response to Post, for which we have no reasonable
        # handler.
        output = yield self.http.Post(data, self.p['module'], '3')
        return self._return('ok')

    # Note the disable function doesn't need wrapping, since it's an
    # alias that does no I/O on its own.
    def disable(self):
        return self.enable(False)

    def _get_status(self):
        """Query the current parameters of this stream from the developer
        interface.  Returns two dicts, (cfg_check, results).

        The "results" are the current parameters read from the
        interface, if found.  If you do not get 'Port', 'Destination',
        'Enabled', be concerned.  The values for 'Running' are drawn
        from ['True', 'False'].

        The "cfg_check" has two entries:

        - 'target_ok' (bool): True if the Destination and Port agree
          with the expected configuration.
        - 'enabled' (bool): True if the stream output seems to be
          currently enabled.

        """
        # Chapter 0 is "Actual Values"
        text = yield self.http.Get(self.p['module'], '0')
        te = soaculib.util.TableExtractor()
        te.feed(text)
        results = te.simple_search(['Running'], 0, 1)

        # Chapter 1 is "Parameters"
        text = yield self.http.Get(self.p['module'], '1')
        te = soaculib.util.TableExtractor()
        te.feed(text)
        results.update(te.simple_search(['Port', 'Destination'], 0, 1))

        # Is that as expected?
        cfg_check = {
            'target_ok': ((results.get('Port') == str(self.p['Port'])) and
                          (results.get('Destination') == self.p['Destination'])),
            'enabled': results.get('Running', 'False') == 'True'}
        return self._return((cfg_check, results))

    def _set_destination(self, destination=None):
        if destination is None:
            destination = self.p['Destination']
        data = {'name': 'Destination', 'value': destination}
        output = yield self.http.Post(data, self.p['module'], '1')
        return self._return('ok')
        
    def _set_port(self, port=None):
        if port is None:
            port = int(self.p['Port'])
        data = {'name': 'Port', 'value': str(port)}
        output = yield self.http.Post(data, self.p['module'], '1')
        return self._return('ok')
        
    def _set_config(self, destination=None, port=None):
        r1 = yield self.set_destination(destination)
        r2 = yield self.set_port(port)
        return self._return((r1, r2))


class ModularHttpInterface:
    """This class implements the basic interface for communicating with
    special functions of the ACU 8100.  These are exposed on a web
    page that appears to be intended for direct user manipulation,
    thus all methods are through Post or Get, with widgets accessed
    through "Module" (which identifies a sub-system, such as
    Services.PositionBroadcast), and "Chapter" (which selects between
    Actual, Parameter, and Target values, and also Commands).

    All the functions here return HttpRequest objects, which should
    then be passed to your preferred backend.

    """
    def __init__(self, base_url, backend=None):
        self.base_url = base_url
        if backend is None:
            backend = soaculib.DebuggingBackend()
        self.backend = backend

    def Get(self, module, chapter=None):
        params = {'Module': module}
        if chapter is not None:
            params['Chapter'] = chapter
        req = soaculib.http.HttpRequest('GET', self.base_url + '/', params)
        return self.backend(req)

    def Post(self, data, module, chapter=None):
        params = {'Module': module}
        if chapter is not None:
            params['Chapter'] = chapter
        req = soaculib.http.HttpRequest('POST', self.base_url + '/', params, data)
        return self.backend(req)



