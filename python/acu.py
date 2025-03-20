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

class AculibError(Exception):
    pass
    
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
        """Upload data to UploadPtStack.  Note data takes precedence over
        filename.  See AcuControl._UploadPtStack for more discussion on these.

        The type_ argument is passed as Type= in the POST; not clear
        if this matters.  The default suffix '\r\n' is to ensure that
        a blank line is included at the end up the upload, since
        otherwise the ACU responds with error (though it accepts the
        valid data into the point stack.)

        """
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

    #: Rate mode sets an axis to move steadily at a certain velocity.
    Rate = 'Rate'

    #: The ElSync mode applies only to 3rd axis on the LAT, and causes
    #: the co-rotator to closesly track the telescope elevation.
    ElSync = 'ElSync'

    #: The Stow mode causes the axes to travel and park at a
    #: particular reference position.
    Stow = 'Stow'

    #: The SurvivalMode is a mode that the ACU transitions to in
    #: certain dire conditions, such as loss of line power or loss of
    #: communication with OCS.
    SurvivalMode = 'SurvivalMode'

    #: MaintenanceStow mode sends the LAT to el=90, and inserts the
    #: stow pin.
    MaintenanceStow = 'MaintenanceStow'

    #: The UnStow mode is used to request that the stow pins be
    #: retracted.
    UnStow = 'UnStow'


class AcuControl:
    """High level interface to ACU platform control.

    """
    def __init__(self, config='guess', backend=None, readonly=False,
                 persistent=False):
        self._config = soaculib.guess_config(config)
        if readonly:
            base_url = self._config['readonly_url']
        else:
            base_url = self._config['base_url']

        backend = soaculib.get_backend(backend, persistent=persistent)
        self.http = AcuHttpInterface(base_url, backend=backend)
        self.streams = soaculib.streams.BroadcastStreamControl.get_all(
            self._config, backend=backend)

        # Decorate all methods for the chosen backend.
        for public_name in ['mode', 'azmode', 'set_elsync', 'set_rate',
                            'go_to', 'go_3rd_axis', 'stop',
                            'clear_faults',
                            'Values', 'Command', 'Write', 'UploadPtStack']:
            func = getattr(self, '_' + public_name)
            setattr(self, '_' + public_name, backend.decorator(func))
            setattr(self, public_name, backend.api_decorator(func))
        # Define the appropriate returnValue function.
        self._return_val_func = backend.return_val_func

    def _return(self, value):
        self._return_val_func(value)

    def _mode(self, mode=None, size=0):
        """Query or set the Antenna.SkyAxes modes.

        To query the modes, pass mode=None (the default).  The modes
        are returned as one or more strings, depending on the value of
        "size".

        If size == 2, then a tuple of values giving the mode of each
        axis is returned.  If size == 1, then a single string is
        returned if the modes are the same, but if they differ then an
        error is raised.  If size == 0 or None, then a tuple or single
        string is returned depending on whether the values differ or
        not.

        To set the mode, pass a mode string or Mode object; or a tuple
        of the same to set the axes to different modes.  Returns a
        success string.

        This function can also access the 3rd axis mode.  It will
        attempt to do in the following cases:

        - mode == None and size == 3: queries all three axis modes and
          returns them as a tuple.
        - mode is a tuple of length 3: all 3 axis modes will be commanded.

        """
        if size is None:
            size = 0
        if isinstance(size, str):
            raise ValueError('The "size" argument should be an int (pass Modes as a tuple?)')

        if mode is None:
            # Query.
            modes = [(yield self.http.Values('Antenna.SkyAxes.Azimuth'))['Mode'],
                     (yield self.http.Values('Antenna.SkyAxes.Elevation'))['Mode']]
            if size == 3:
                # SkyAxes.3rdAxis is renamed to Polarisation in latest SAT and LAT XMLs
                modes.append(
                    (yield self.http.Values('Antenna.SkyAxes.Polarisation'))['Mode'])

            # Package for return.
            return_all = (modes[0] != modes[1]) or size >= 2
            if return_all and size == 1:
                raise AculibError(f'Modes differ!: {modes[0]}, {modes[1]}')
            if return_all:
                result = tuple(modes)
            else:
                result = modes[0]
        elif isinstance(mode, (Mode, str)):
            mode = Mode(mode)
            result = yield self.http.Command(
                'DataSets.CmdModeTransfer', 'SetAzElMode', mode.value)
        else:
            assert(len(mode) in [2, 3])
            if any([m is None for m in mode]):
                # Fill in the missing ones.
                _mode = (yield self.mode(size=len(mode)))
                mode = [b if a is None else a
                        for a, b in zip(mode, _mode)]
            modes = [Mode(m).value for m in mode]
            result = yield self.http.Command(
                'DataSets.CmdModeTransfer', 'SetModes', modes)
        self._return(result)

    def _azmode(self, mode=None):
        """Set the Antenna.SkyAxes mode for the Azimuth axis and set the
        Antenna.SkyAxes mode for the Elevation axis to Stop.

        To set the mode, pass a mode string or Mode object.  Returns a
        success string.
        """
        mode = Mode(mode)
        result = yield self.http.Command(
            'DataSets.CmdModeTransfer', 'SetModes', [mode.value, 'Stop'])
        self._return(result)

    def _go_to(self, az=None, el=None, set_mode=True):
        """Optionally update the Preset position target (az, el, neither, or
        both) and then change some axes to Preset mode (see note below).

        Returns after the last command, which is probably well before
        the motion itself has completed.

        Note how this function changes the axis modes:
        - if set_mode=False, the axis modes are not changed.
        - if set_mode=True, both axis modes are changed to Preset.
        - if set_mode='target', *only* the axes for which a new target
          position was specified will have their mode updated.

        """
        # Set the position first, then the mode.  Otherwise you might
        # rush to some random position (e.g. if ACU just rebooted).
        result = None
        modes = [None, None]
        if az is not None or el is not None:
            cmd, par = [], []
            if az is not None:
                cmd.append('Azimuth')
                par.append('%.4f' % az)
                modes[0] = 'Preset'
            if el is not None:
                cmd.append('Elevation')
                par.append('%.4f' % el)
                modes[1] = 'Preset'
            result = yield self.http.Command(
                'DataSets.CmdAzElPositionTransfer',
                'Set ' + ' '.join(cmd), par)

        if set_mode in ['target']:
            if any([m is not None for m in modes]):
                result = yield self._mode(modes)
        elif set_mode:
            result = yield self._mode('Preset')
        else:
            pass

        self._return(result)

    def _set_elsync(self):
        result = yield self.http.Command(
            'DataSets.CmdModeTransfer', 'Set3rdAxisMode', 'ElSync')
        self._return(result)

    def _set_rate(self, az=None, el=None, third=None,
                  set_mode=True):
        """
        Put one or more axes into "Rate" mode, and set the rates.


        """
        vel_sets = {
            'az': ('DataSets.CmdAzElVelocityTransfer8100', 'Set Azimuth'),
            'el': ('DataSets.CmdAzElVelocityTransfer8100', 'Set Elevation'),
            'th': ('DataSets.Cmd3rdAxisVelocityTransfer', 'Set Polarization'),
        }
        modes = {
            'az': None,
            'el': None,
            'th': None,
        }

        for axis, val in [('az', az), ('el', el), ('th', third)]:
            if val is None or val is False:
                continue
            if isinstance(val, (float, int)):
                ds, name = vel_sets[axis]
                result = yield self.http.Command(ds, name, '%f' % val)
                print(result)
            if val is True or set_mode:
                modes[axis] = 'Rate'
        # If third mode is None, drop it ...
        if modes['th'] is None:
            del modes['th']
        # If either of the other two are None, backfill them.
        if modes['az'] is None or modes['el'] is None:
            cur_modes = yield self._mode(None, size=2)
            if modes['az'] is None:
                modes['az'] = cur_modes[0]
            if modes['el'] is None:
                modes['el'] = cur_modes[1]
        yield self._mode([v for v in modes.values()])

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

    def _clear_faults(self):
        """Clear any axis faults (Failure Reset)."""
        result = yield self.http.Command('DataSets.CmdGeneralTransfer',
                                         'Failure Reset')
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
