import numpy as np
import time
import datetime as dt
from scipy.interpolate import CubicSpline, interp1d
import server_keys as sk
from threading import Thread

TZ = dt.timezone.utc


def find_day_of_year(now):
    """Compute an ACU "Day" value, which is a timestamp computed as
    (fractional) days since the start of the current year, starting
    from 1.

    Input: now (datetime object, datetime.datetime.now())

    Returns: tuple (Day, Integer, Fraction) where Integer is the
      integer day number, Fraction is the fractional part (0 <=
      Fraction < 1) and Time is the sum of the two.

    """
    day_of_year = now.timetuple().tm_yday
    seconds = ((now.hour) * 60 * 60 + now.minute * 60 + now.second + now.microsecond * 1e-6)
    day_part = seconds / (24 * 60 * 60)
    acu_day = day_of_year + day_part
    return acu_day, day_of_year, seconds

def initialize_data_dict(dataset, set_time=True, set_defaults=True):
    """Load server keys from module and populate with sensible starting values.

    Args:
        dataset (str): Name of dataset, i.e. 'Datasets.StatusSATPDetailed8100'
        set_time (bool): If True, include date/time in the dataset.
        set_defaults (bool): If True, treat this is the main "general" dataset
             and put in the starting positions.

    Returns:
        dict: Data dictionary with all values initialized.

    """
    data = {}
    for key, val in sk.status_fields[dataset].items():
        if val == int:
            data[key] = 0
        elif val == bool:
            data[key] = False
        elif val == str:
            data[key] = 'Stop'
        elif val == float:
            data[key] = 0.0

    if set_time:
        init_now = dt.datetime.now(TZ)
        init_time, init_day, init_hms = find_day_of_year(init_now)
        data['Day'] = init_day
        data['Time_UDP'] = init_hms
        data['Year'] = init_now.year
        data['Time'] = init_time

    if set_defaults:
        data['Azimuth current position'] = 90.
        data['Raw Azimuth'] = 90.
        data['Corrected Azimuth'] = 90.
        data['Elevation current position'] = 90.
        data['Raw Elevation'] = 90.
        data['Corrected Elevation'] = 90.
        data['Boresight current position'] = 10.
        data['Raw Boresight'] = 10.
        data['Corrected Boresight'] = 10.

        data['ACU in remote mode'] = True

    return data


class DataMaster:
    """ACU Data container class.

    Attributes:
        data (dict): Dictionary tracking values of internal data registers.
        queue (dict): Acts as the stack of points being uploaded via
            UploadPtStack.
        running (bool): True if currently running a track (via run_track()),
            False if not running.

    Args:
        dataset (str): Name of dataset, i.e. 'Datasets.StatusSATPDetailed8100'

    """
    def __init__(self, dataset):
        self.data = initialize_data_dict(dataset)
        self.queue = self._initialize_queue()
        self.running = False

    @staticmethod
    def _initialize_queue():
        queue = {'times': [],
                 'azs': [],
                 'els': [],
                 'azflags': [],
                 'free': 10000}

        return queue

    def clear_queue(self):
        """Clear the queue by reinitializing it as empty.

        If we're clearing the queue it's likely because we're trying to stop
        motion, so also set self.running to False, and set the velocity to zero.
        """
        self.queue = self._initialize_queue()
        self.running = False
        self.update_data('Azimuth current velocity', 0.)  # Since we've stopped

    def update_timestamp(self):
        """Update 'Day', 'Time_UDP', Year', and 'Time' fields in data dict with
        the current time.

        """
        now = dt.datetime.now(TZ)
        nowtime, nowday, nowhms = find_day_of_year(now)
        self.data['Day'] = nowday
        self.data['Time_UDP'] = nowhms
        self.data['Year'] = now.year
        self.data['Time'] = nowtime

    def update_positions(self, new_az=None, new_el=None, new_bs=None):
        if new_az is not None:
            self.data['Azimuth current position'] = new_az
            self.data['Raw Azimuth'] = new_az
            self.data['Corrected Azimuth'] = new_az
        if new_el is not None:
            self.data['Elevation current position'] = new_el
            self.data['Raw Elevation'] = new_el
            self.data['Corrected Elevation'] = new_el
        if new_bs is not None:
            self.data['Boresight current position'] = new_bs
            self.data['Raw Boresight'] = new_bs
            self.data['Corrected Boresight'] = new_bs

    def update_data(self, key, new_value=None):
        if isinstance(key, dict):
            assert new_value is None
            self.data.update(key)
        else:
            self.data[key] = new_value

    def update_queue(self):
        """Update the queue, primarily to track the uploaded point stack."""
        self.queue['free'] = 10000 - len(self.queue['times'])
        self.update_data('Qty of free program track stack positions', self.queue['free'])

    def _run_preset_thread(self):

        target = None
        all_data = {
            'Azimuth': {
                'target': None,
                'speed': 6.,
            },
            'Elevation': {
                'target': None,
                'speed': 6.,
            },
            'Boresight': {
                'target': None,
                'speed': 1.,
            },
        }

        while True:
            now = time.time()
            active_axes = []
            for axis, data in all_data.items():
                if self.data[f'{axis} mode'] != 'Preset':
                    # Clear the target on mode transition to make sure
                    # you repopulate state.
                    data['target'] = None
                    continue
                active_axes.append(axis)

                # Move towards the target position.
                current_pos = self.data[f'Raw {axis}']
                new_target = self.data[f'{axis} commanded position']
                if data['target'] is None or data['target'] != new_target:
                    # Motion plan ...
                    speed = data['speed']
                    data.update({
                        'target': new_target,
                        'start_time': now,
                        'start_pos': current_pos,
                        'end_time': abs(new_target - current_pos) / speed + now,
                        'vel': np.sign(new_target - current_pos) * speed,
                    })

                if current_pos != data['target']:
                    if now >= data['end_time']:
                        data['pos'] = data['target']
                        data['vel'] = 0.
                    else:
                        data['pos'] = data['start_pos'] + data['vel'] * (now - data['start_time'])

            if len(active_axes):
                self.update_timestamp()
                _up_pos = {}
                _up_dat = {}
                if 'Azimuth' in active_axes:
                    _up_pos['new_az'] = all_data['Azimuth'].get('pos')
                    v_az = all_data['Azimuth'].get('vel', 0.)
                    _up_dat.update({
                        'Azimuth Current 1': v_az * (0.5 + 0.01 * np.random.random()),
                        'Azimuth Current 2': v_az * (0.5 + 0.01 * np.random.random()),
                        'Azimuth current velocity': v_az,
                    })
                if 'Elevation' in active_axes:
                    _up_pos['new_el'] = all_data['Elevation'].get('pos')
                    v_el = all_data['Elevation'].get('vel', 0.)
                    _up_dat.update({
                        'Elevation Current 1': v_el * (0.5 + 0.01 * np.random.random()),
                        'Elevation current velocity': v_el,
                    })
                if 'Boresight' in active_axes:
                    _up_pos['new_bs'] = all_data['Boresight'].get('pos')

                self.update_positions(**_up_pos)
                self.update_data(_up_dat)
                time.sleep(0.001)

            else:
                time.sleep(0.1)

    def preset_azel_motion(self, new_az=None, new_el=None):
        """Update the target positions for az, el or boresight.  When
        in Preset mode, simulator will seek to those positions at
        constant velcocity.

        """
        if new_az is not None:
            self.data['Azimuth commanded position'] = new_az
        if new_el is not None:
            self.data['Elevation commanded position'] = new_el
        return True

    def preset_bs_motion(self, new_bs):
        self.data['Boresight commanded position'] = new_bs

    def change_mode(self, axes=[], modes=[]):
        if len(axes) != len(modes):
            return
        for i in range(len(axes)):
            self.data[axes[i] + " mode"] = modes[i]
            if modes[i] == 'Stop':
                self.data[axes[i] + " brakes released"] = False
            elif modes[i] == 'Preset':
                self.data[axes[i] + " brakes released"] = True

    @staticmethod
    def _calculate_udp_time(line):
        """Calculate the UDP Time for a give line uploaded to the queue.

        For more on the format see `upload_track()`.

        Args:
            line (str): Single decoded line from queue.

        """
        # Example: '168, 19:11:22.342642; 27.414830; 35.000000; ...'
        acutime = line.split(';')[0]
        #day = int(acutime.split(', ')[0])
        utime = acutime.split(', ')[1]
        hr = float(utime.split(':')[0])
        mn = float(utime.split(':')[1])
        sc = float(utime.split(':')[2])
        timeudp = hr * 60. * 60. + mn * 60. + sc
        return timeudp

    def upload_track(self, lines):
        """Upload a track to the queue.

        Args:
            lines (bytes): 'utf-8' bytes encoded string with points to add to
                the queue. Delimited by '\r\n'.

        Examples:
            An example of a single line for upload::

                $ lines = b'168, 19:11:22.342642; 27.414830; 35.000000; 2.0000; 0.0000; 1; 0\r\n'

        """
        # if we make a PointStack object that's a (or several) queue.Queue(s)
        # we can just .put() each item into the appropriate queue during the
        # for loop. Need to understand how the point are used in run_track() first
        slines = lines.decode('utf-8')
        linelist = slines.split('\r\n')
        udptimes = []
        azpts = []
        elpts = []
        azflags = []
        for line in linelist:
            # print(line)
            if len(line):
                #   day, utime;           azimuth    elevation  ?       ?       azflag  ?
                # b'168, 19:11:22.342642; 27.414830; 35.000000; 2.0000; 0.0000; 1;      0\r\n'
                # we want, 'times', 'azs', 'els', 'azflags' out of this

                # 'times'
                timeudp = self._calculate_udp_time(line)
                udptimes.append(timeudp)

                # 'az/el/flag'
                azpt = float(line.split(';')[1])
                elpt = float(line.split(';')[2])
                azflag = int(line.split(';')[5])
                azpts.append(azpt)
                elpts.append(elpt)
                azflags.append(azflag)

        # print(self.queue)
        # print('udptimes len: '+str(len(udptimes)))
        # print('azflags len: ' + str(len(azflags)))
        self.queue['times'].extend(udptimes)
        self.queue['azs'].extend(azpts)
        self.queue['els'].extend(elpts)
        self.queue['azflags'].extend(azflags)

        self.queue['free'] = 10000 - len(self.queue['times'])
        self.update_data('Qty of free program track stack positions', self.queue['free'])
        print('times', len(self.queue['times']))
        print('azs', len(self.queue['azs']))
        print('els', len(self.queue['els']))
        print('azflags', len(self.queue['azflags']))

    def _update_queue_view(self, group, width):
        keys = ['times', 'azs', 'els', 'azflags']
        for key in keys:
            group[key].append(self.queue[key].pop(0))
            self.queue['free'] += 1
            if len(group[key]) > width:
                group[key].pop(0)

    def _compute_velocity(self, times, posfit):
        """Compute velocities for a given axis.

        Since we're only looking at four points, and the positions during
        turnarounds are entirely from fits, we use the position fit to first
        generate positions at a reasonable time spacing. Then take the gradient
        of those positions. Finally, fit those results, and return the fit.

        Args:
            times (list): Times from the interpolation group
            posfit (scipy.interpolate Object): Position fit, valid for the
                given times. Used to generate positions to compute velocity
                from.

        Returns:
            scipy.interpolate._cubic.CubicSpline: CubicSpline fit for
            velocities, valid for the times given in the input args.

        """
        # This spacing is sort of arbitrary. Trying to capture enough points
        # that we get a good estimate of the velocity, without computing too
        # many.
        t_spacing = np.mean(np.diff(times))/10
        vel_times = np.arange(times[0], times[-1], t_spacing)
        az_pos = posfit(vel_times)
        vels = np.gradient(az_pos, t_spacing)
        velfit = CubicSpline(vel_times, vels)

        return velfit

    def run_track(self):
        modes = [self.data['Azimuth mode'], self.data['Elevation mode']]
        if modes[0] != 'ProgramTrack':
            return False

        self.running = True

        # queue starts as empty set of 4 empty lists, and the number of free spaces (10000)
        queue = self.queue

        # only look at this many points from the queue at a time
        # Note: below code isn't general enough for this to change without other work
        VIEW_WIDTH = 4

        # initialize the group of points we'll use for interpolations
        # Idea here is to only every let this be 4 long, and use that group for the interpolations
        interp_group = {'times': [], 'azs': [], 'els': [], 'azflags': []}
        for i in range(VIEW_WIDTH):
            self._update_queue_view(interp_group, VIEW_WIDTH)

        while len(queue['times']):
            try:
                self._update_queue_view(interp_group, VIEW_WIDTH)
            except IndexError:
                print("Queue is empty, likely trying to stop a run.")
                break

            # Skip the group after a turnaround group [1, 2, 1, 1]
            # Note: If VIEW_WIDTH ever changes, this'll need more thought,
            # you'll want to skip another group for every +2 increase in
            # VIEW_WIDTH
            if interp_group['azflags'][0] == 2:
                continue

            fittimes = interp_group['times']
            fitazs = interp_group['azs']
            fitels = interp_group['els']

            if interp_group['azflags'] != [1, 2, 1, 1]:
                # linear interpolation between normal points in a scan
                azfit = interp1d(fittimes, fitazs, fill_value="extrapolate")
                elfit = interp1d(fittimes, fitels, fill_value="extrapolate")
                valid_until = fittimes[1]
            else:
                # cubic spline interpolation for turnarounds
                try:
                    azfit = CubicSpline(fittimes, fitazs)
                    elfit = CubicSpline(fittimes, fitels)
                    valid_until = fittimes[int(VIEW_WIDTH/2)]
                except ValueError:
                    print('Error in CubicSpline computation', flush=True)
                    print('TIMES:', fittimes, flush=True)
                    print('AZ:', fitazs, flush=True)
                    print('EL:', fitels, flush=True)
                    raise ValueError

            velfit = self._compute_velocity(fittimes, azfit)

            # wait until beginning of the interp_group times
            nowtime = self.data['Time_UDP']
            while nowtime < fittimes[0]:
                time.sleep(0.001)
                nowtime = self.data['Time_UDP']

            # apply our interpolation and update the self.data object's
            # positions and timestamps within the time the fit is valid for
            while nowtime < valid_until:
                ptrack = [m == 'ProgramTrack' for m in
                          [self.data['Azimuth mode'], self.data['Elevation mode']]]
                try:
                    newaz, newel = None, None
                    if ptrack[0]:
                        newaz = float(azfit(nowtime))
                        self.update_data('Azimuth current velocity', float(velfit(nowtime)))
                    if ptrack[1] == 'ProgramTrack':
                        newel = float(elfit(nowtime))
                    self.update_positions(new_az=newaz, new_el=newel)
                    self.update_timestamp()
                    nowtime = self.data['Time_UDP']
                except ValueError:
                    time.sleep(0.001)
                    nowtime = self.data['Time_UDP']

        # this'll be true except when we're trying to abort a scan
        if self.running:
            # final_stretch
            landing = {'times': [], 'azs': [], 'els': [], 'azflags': []}
            offset = 0.5  # realistic settling time, but won't produce as large an
                          # amplitude in the settling motion (which would be ~0.8 deg)
            for i in range(4):
                landing['times'].append(interp_group['times'][-1] + np.median(np.diff(interp_group['times']))*(i+1) + offset)
                landing['azs'].append(interp_group['azs'][-1])
                landing['els'].append(interp_group['els'][-1])
                landing['azflags'].append(1)
            interp_group['times'].extend(landing['times'])
            interp_group['azs'].extend(landing['azs'])
            interp_group['els'].extend(landing['els'])
            interp_group['azflags'].extend(landing['azflags'])

            azfit = CubicSpline(interp_group['times'], interp_group['azs'])
            elfit = CubicSpline(interp_group['times'], interp_group['els'])
            velfit = self._compute_velocity(interp_group['times'], azfit)

            nowtime = self.data['Time_UDP']
            while nowtime < interp_group['times'][-1]:
                newaz = float(azfit(nowtime))
                newel = float(elfit(nowtime))
                self.update_positions(newaz, newel, self.data['Raw Boresight'])
                self.update_data('Azimuth current velocity', float(velfit(nowtime)))
                # time.sleep(0.0001)
                self.update_timestamp()
                nowtime = self.data['Time_UDP']

        # Ensures queue is empty, and velocity set to zero
        self.clear_queue()

        return True

    def values(self):
        """Update and return the data dict.

        This is called each time the /Values endpoint is hit on the simulator
        server.

        Returns:
            dict: The full data dict.

        """
        return self.data

    def _run_background_updates(self):
        while True:
            self.update_timestamp()
            self.update_queue()
            time.sleep(0.02)

    def run(self):
        """Run background updates.

        This starts a thread that continuously updates the timestamps and
        queue, and should be called after initialization.

        """
        update_thread = Thread(target=self._run_background_updates)
        update_thread.start()
        preset_thread = Thread(target=self._run_preset_thread)
        preset_thread.start()
