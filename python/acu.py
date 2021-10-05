import soaculib
import enum
import os

class ValuesType(enum.Enum):
    Actual = 'Actual'
    Target = 'Target'
    Parameter = 'Parameter'

class ValuesFormat(enum.Enum):
    ASCII = 'ASCII'
    Binary = 'Binary'
    HTML = 'HTML'
    JSON = 'JSON'
    SSV = 'SSV'
    XML = 'XML'

class DocumentationType(enum.Enum):
    actual = 'actual'
    target = 'target'
    parameter = 'parameter'
    commands = 'commands'
    
class AcuHttpInterface:
    """This class constructs HTTP requests of the kind described in the
    ACU ICD.  There is a method defined for each of the main "Plugins"
    (Values, Command, Write).  In each case the first argument is the
    Module identifier.

    Each Plugin function constructs a single HttpRequest object.  If a
    preferred Backend has not been set up, then the Plugin functions
    return the HttpRequest object to the user (without making any HTTP
    request).  If a backend has been set, then self.backend(request)
    is returned (and so it's likely the request has been initiated, if
    not completed).  Depending on the backend in use, the result might
    be a Deferred object, or the decoded result.

    """
    def __init__(self, base_url, backend=None):
        self.base_url = base_url
        if backend is None:
            backend = soaculib.DebuggingBackend()
        self.backend = backend

    def Values(self, identifier, type_='Actual', format_='JSON'):
        type_ = ValuesType(type_) # validate
        format_ = ValuesFormat(format_) # validate
        req = soaculib.http.HttpRequest(
            'GET', self.base_url + '/Values', {
                'identifier': identifier,
                'type': type_.name,
                'format': format_.name},
            decoder='json')
        return self.backend(req)

    def Command(self, identifier, command, parameter=None):
        if isinstance(parameter, list):
            parameter = '|'.join(parameter)
        http_params = {
            'identifier': identifier,
            'command': command,
        }
        if parameter is not None:
            http_params['parameter'] = parameter
        req = soaculib.http.HttpRequest(
            'GET', self.base_url + '/Command', http_params)
        return self.backend(req)

    def Write(self, identifier, data):
        req = soaculib.http.HttpRequest(
            'POST', self.base_url + '/Write',
            {'identifier': identifier}, data)
        return self.backend(req)

    def Documentation(self, identifier, type_='actual'):
        """Query the "Documentation" Plugin for the specified identifier (and
        type).  Returns an HTML table describing the module.

        """
        type_ = DocumentationType(type_) # validate
        req = soaculib.http.HttpRequest(
            'GET', self.base_url + '/Documentation', {
                'identifier': identifier,
                'type': type_.name})
        return self.backend(req)

    def Meta(self):
        """Query the "Meta" Plugin.  This takes no parameters.  Returns XML
        describing the tree.

        """
        req = soaculib.http.HttpRequest(
            'GET', self.base_url + '/Meta', {})
        return self.backend(req)

    def Version(self):
        """Query the "Version" Plugin.  Takes no parameters, returns line format."""
        req = soaculib.http.HttpRequest(
            'GET', self.base_url + '/Version', {})
        return self.backend(req)

    def UploadPtStack(self, data=None, filename=None, type_='File', suffix='\r\n'):
        if filename is None:
            filename = 'UploadedFromBrowser'
        elif data is None:
            # Read lines from file and upload them.
            data = open(filename, 'rb').read().decode('utf8')
            filename = os.path.split(filename)[1]
        req = soaculib.http.HttpRequest(
            'POST', self.base_url + '/UploadPtStack',{'Type':type_, 'filename':filename},
            data=data + suffix)
        return self.backend(req)

class Mode(enum.Enum):
    """Some operating Modes of the ACU.

    """

    #: The Stop mode is an idle state from which active axis modes may
    #: be set.
    Stop = 'Stop'

    #: The Preset mode means that the axis is moving to or holding a
    #: fixed position.
    Preset = 'Preset'

    #: The ProgramTrack mode is a mode where the axis is travelled
    #: through a series of positions uploaded continuously to the ACU.
    ProgramTrack = 'ProgramTrack'

    #: The Stow mode causes the axes to travel and park at a
    #: particular reference position.
    Stow = 'Stow'

    #: The SurvivalMode is a mode that the ACU transitions to in
    #: certain dire conditions, such as loss of line power or loss of
    #: communication with OCS.
    SurvivalMode = 'SurvivalMode'


class AcuControl:
    """High level interface to ACU platform control.

    """
    def __init__(self, config='guess', backend=None, readonly=False):
        self._config = soaculib.guess_config(config)
        if readonly:
            base_url = self._config['readonly_url']
        else:
            base_url = self._config['base_url']

        backend = soaculib.get_backend(backend)
        self.http = AcuHttpInterface(base_url, backend=backend)
        self.streams = soaculib.streams.BroadcastStreamControl.get_all(
            self._config, backend=backend)

        # Decorate all methods for the chosen backend.
        for public_name in ['mode', 'go_to', 'go_3rd_axis', 'stop',
                            'Values', 'Command', 'Write', 'UploadPtStack']:
            func = getattr(self, '_' + public_name)
            setattr(self, '_' + public_name, backend.decorator(func))
            setattr(self, public_name, backend.api_decorator(func))
        # Define the appropriate returnValue function.
        self._return_val_func = backend.return_val_func

    def _return(self, value):
        self._return_val_func(value)

    def _mode(self, mode=None):
        """Query or set the Antenna.SkyAxes modes.

        To query the mode, pass mode=None (the default).  Then this
        function returns a single string describing the mode, unless
        the two axes have different modes in which case a tuple of
        strings is returned.

        To set the mode, pass a mode string or Mode object.  Returns a
        success string.

        """
        if mode is None:
            # Query.
            mode0 = (yield self.http.Values('Antenna.SkyAxes.Azimuth'))['Mode']
            mode1 = (yield self.http.Values('Antenna.SkyAxes.Elevation'))['Mode']
            # Return:
            if mode0 != mode1:
                self._return((mode0, mode1))
            else:
                self._return(mode0)
        mode = Mode(mode)
        result = yield self.http.Command(
            'DataSets.CmdModeTransfer', 'SetAzElMode', mode.value)
        self._return(result)

    def _go_to(self, az=None, el=None):
        """Change to Preset mode and move to the specified position.  If a
        coordinate is omitted, no motion will be initiated on that
        axis.

        Returns when the motion commands have been issued, which is
        probably well before when the motion itself has completed.

        """
        yield self._mode('Preset')
        if az is None and el is None:
            return
        cmd, par = [], []
        if az is not None:
            cmd.append('Azimuth')
            par.append('%.4f' % az)
        if el is not None:
            cmd.append('Elevation')
            par.append('%.4f' % el)
        result = yield self.http.Command(
            'DataSets.CmdAzElPositionTransfer',
            'Set ' + ' '.join(cmd), par)
        self._return(result)

    def _go_3rd_axis(self, val):
        """Change 3rd axis to Preset mode and move to specified position.

        Returns when the motion commands have been issued, which is
        probably well before when the motion itself has completed.

        """
        # Send position first...
        result = yield self.http.Command(
            'DataSets.Cmd3rdAxisPositionTransfer',
            'Set Polarization', '%.4f' % val)
        # Check the results...
        # Set mode.
        yield self.http.Command(
            'DataSets.CmdModeTransfer', 'Set3rdAxisMode', 'Preset')
        self._return(result)

    def _stop(self):
        """Special request to set all axes, including 3rd Axis, to Stop mode.

        """
        result = yield self.http.Command(
            'DataSets.CmdModeTransfer', 'Stop')
        self._return(result)

    # Pass-throughs for plugin primitives
    def _Values(self, identifier, type_='Actual', format_='JSON'):
        """See documentation for AcuHttpInterface.Values."""
        return (yield self.http.Values(identifier, type_, format_))

    def _Command(self, identifier, command, parameter=None):
        """See documentation for AcuHttpInterface.Command."""
        return (yield self.http.Command(identifier, command, parameter))

    def _Write(self, identifier, data):
        """See documentation for AcuHttpInterface.Write."""
        return (yield self.http.Write(identifier, data))

    def _UploadPtStack(self, data=None, filename=None):
        """Send ProgramTrack points to the ACU through the UploadPtStack form.

        Args:
          data (str): The program track data to send.  This takes
            precedence over "filename", if both are passed.  We know
            the ACU works with DOS line endings, so be cautious and
            use those.

          filename (str): If data is not None, then this is simply the
            filename to provide to the ACU (defaults to
            "UploadedFromBrowser".  But if data is None, then the
            specified file will be read from the local filesystem and
            that data will be uploaded.

        """
        return (yield self.http.UploadPtStack(data=data, filename=filename))
