import numpy as np
import time
import datetime as dt
from scipy.interpolate import CubicSpline, interp1d
import server_keys as sk
from threading import Thread

TZ = dt.timezone.utc


def find_day_of_year(now):
    """
    Function to find the current day of the year.

    Input: now (datetime object, datetime.datetime.now())

    Returns: current time as a portion of a day of the year
    """
    months = {1: 31, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    year = now.year
    if year % 4 == 0:
        months[2] = 29
    else:
        months[2] = 28
    current_day_of_year = 0
    for i in range(1, now.month):
        current_day_of_year += months[i]
    current_day_of_year += now.day
    current_hms = ((now.hour) * 60 * 60 + now.minute * 60 + now.second + now.microsecond * 1e-6)
    current_day_part = current_hms / (24 * 60 * 60)
    current_time = current_day_of_year + current_day_part
    return current_time, current_day_of_year, current_hms


def _initialize_data_dict(dataset):
    """Load server keys from module and populate with sensible starting values.

    Args:
        dataset (str): Name of dataset, i.e. 'Datasets.StatusSATPDetailed8100'

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

    init_now = dt.datetime.now(TZ)
    init_time, init_day, init_hms = find_day_of_year(init_now)
    data['Day'] = init_day
    data['Time_UDP'] = init_hms
    data['Year'] = init_now.year
    data['Time'] = init_time
    data['Azimuth current position'] = 90.
    data['Raw Azimuth'] = 90.
    data['Corrected Azimuth'] = 90.
    data['Elevation current position'] = 90.
    data['Raw Elevation'] = 90.
    data['Corrected Elevation'] = 90.
    data['Boresight current position'] = 10.
    data['Raw Boresight'] = 10.
    data['Corrected Boresight'] = 10.

    return data


class DataMaster:
    """ACU Data container class.

    Attributes:
        data (dict): Dictionary tracking values of internal data registers.
        queue (dict): Acts as the stack of points being uploaded via
            UploadPtStack.

    Args:
        dataset (str): Name of dataset, i.e. 'Datasets.StatusSATPDetailed8100'

    """
    def __init__(self, dataset):
        self.data = _initialize_data_dict(dataset)
        self.queue = self._initialize_queue()

    @staticmethod
    def _initialize_queue():
        queue = {'times': [],
                 'azs': [],
                 'els': [],
                 'azflags': [],
                 'free': 10000}

        return queue

    def clear_queue(self):
        """Clear the queue by reinitializing it as empty."""
        self.queue = self._initialize_queue()

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

    def update_positions(self, new_az, new_el, new_bs):
        self.data['Azimuth current position'] = new_az
        self.data['Raw Azimuth'] = new_az
        self.data['Corrected Azimuth'] = new_az
        self.data['Elevation current position'] = new_el
        self.data['Raw Elevation'] = new_el
        self.data['Corrected Elevation'] = new_el
        self.data['Boresight current position'] = new_bs
        self.data['Raw Boresight'] = new_bs
        self.data['Corrected Boresight'] = new_bs

    def update_data(self, key, new_value):
        self.data[key] = new_value

    def update_queue(self):
        """Update the queue, primarily to track the uploaded point stack."""
        self.queue['free'] = 10000 - len(self.queue['times'])
        self.update_data('Qty of free program track stack positions', self.queue['free'])

    def preset_azel_motion(self, new_az, new_el):
        current_azmode = self.data['Azimuth mode']
        current_elmode = self.data['Elevation mode']
        if current_azmode != 'Preset' or current_elmode != 'Preset':
            return
        current_az = self.data['Raw Azimuth']
        current_el = self.data['Raw Elevation']
        if current_az > new_az:
            azvel = -6.0
        elif current_az < new_az:
            azvel = 6.0
        else:
            azvel = 0.0
        if current_el > new_el:
            elvel = -6.0
        elif current_el < new_el:
            elvel = 6.0
        else:
            elvel = 0.0
        current_time = self.data['Time_UDP'] + 5.
        initial_times = np.linspace(current_time - 5., current_time - 0.01, num=10)
        initial_azs = np.zeros(10) + current_az
        initial_els = np.zeros(10) + current_el
        if azvel != 0.0:
            elapsed_time_az = abs((current_az - new_az) / azvel)
        else:
            elapsed_time_az = 10
        if elvel != 0.0:
            elapsed_time_el = abs((current_el - new_el) / elvel)
        else:
            elapsed_time_el = 10
        endtime_az = current_time + elapsed_time_az
        endtime_el = current_time + elapsed_time_el
        azs = np.linspace(current_az, new_az, num=50)
        els = np.linspace(current_el, new_el, num=50)
        aztimes = np.linspace(current_time, endtime_az, num=50)
        eltimes = np.linspace(current_time, endtime_el, num=50)
        if max(aztimes) > max(eltimes):
            missingtime_ixs = np.where(aztimes > max(eltimes))[0]
            for ix in missingtime_ixs:
                eltimes = np.append(eltimes, aztimes[ix])
                els = np.append(els, new_el)
        elif max(aztimes) < max(eltimes):
            missingtime_ixs = np.where(eltimes > max(aztimes))[0]
            for ix in missingtime_ixs:
                aztimes = np.append(aztimes, eltimes[ix])
                azs = np.append(azs, new_az)
        else:
            pass
        aztimes = np.concatenate((initial_times, aztimes))
        eltimes = np.concatenate((initial_times, eltimes))
        azs = np.concatenate((initial_azs, azs))
        els = np.concatenate((initial_els, els))

        azslopes = []
        elslopes = []
        for i in range(1, len(azs)):
            aslope = (azs[i] - azs[i - 1]) / (aztimes[i] - aztimes[i - 1])
            azslopes.append(aslope)
        for j in range(1, len(els)):
            eslope = (els[j] - els[j - 1]) / (eltimes[j] - eltimes[j - 1])
            elslopes.append(eslope)

        azcurve = CubicSpline(aztimes, azs)
        elcurve = CubicSpline(eltimes, els)
        azslopecurve = CubicSpline(aztimes[1:], azslopes)
        elslopecurve = CubicSpline(eltimes[1:], elslopes)

        nowtimestamp = current_time
        while nowtimestamp < max(aztimes):
            self.update_timestamp()
            input_az = float(azcurve(nowtimestamp))
            input_el = float(elcurve(nowtimestamp))
            self.update_positions(input_az, input_el, self.data['Raw Boresight'])
            if azvel > 0:
                self.update_data('Azimuth Current 1', 3 + 0.1 * np.random.random())
                self.update_data('Azimuth Current 2', 3 + 0.1 * np.random.random())
            if azvel < 0:
                self.update_data('Azimuth Current 1', -1 * (3 + 0.1 * np.random.random()))
                self.update_data('Azimuth Current 2', -1 * (3 + 0.1 * np.random.random()))
            if elvel > 0:
                self.update_data('Elevation Current 1', (3 + 0.1 * np.random.random()))
            if elvel < 0:
                self.update_data('Elevation Current 1', -1 * (3 + 0.1 * np.random.random()))
            if nowtimestamp == current_time:
                self.update_data('Azimuth current velocity', azvel)
                self.update_data('Elevation current velocity', elvel)
            elif nowtimestamp != current_time:
                self.update_data('Azimuth current velocity', float(azslopecurve(nowtimestamp)))
                self.update_data('Elevation current velocity', float(elslopecurve(nowtimestamp)))
            time.sleep(0.001)
            nowtimestamp = self.data['Time_UDP']
        self.update_timestamp()
        self.update_positions(new_az, new_el, self.data['Raw Boresight'])
        self.update_data('Elevation Current 1', 0.0)
        self.update_data('Azimuth Current 1', 0.0)
        self.update_data('Azimuth Current 2', 0.0)
        self.update_data('Elevation current velocity', 0.0)
        self.update_data('Azimuth current velocity', 0.0)
        return True

    def change_mode(self, axes=[], modes=[]):
        if len(axes) != len(modes):
            return
        for i in range(len(axes)):
            self.data[axes[i] + " mode"] = modes[i]

    def preset_bs_motion(self, new_bs):
        current_bs = self.data['Raw Boresight']
        if current_bs > new_bs:
            bsvel = -6.0
        elif current_bs < new_bs:
            bsvel = 6.0
        else:
            bsvel = 0.0
        current_time = self.data['Time_UDP']
        if bsvel != 0.0:
            elapsed_time_bs = abs((new_bs - current_bs) / bsvel)
        else:
            elapsed_time_bs = 1.
        endtime_bs = current_time + elapsed_time_bs
        bss = np.linspace(current_bs, new_bs, num=50)
        bstimes = np.linspace(current_time, endtime_bs, num=50)
        bscurve = CubicSpline(bstimes, bss)
        nowtimestamp = current_time
        while nowtimestamp < endtime_bs:
            self.update_timestamp()
            self.update_positions(
                self.data['Raw Azimuth'],
                self.data['Raw Elevation'],
                float(
                    bscurve(nowtimestamp)))
            nowtimestamp = self.data['Time_UDP']
        self.update_timestamp()
        self.update_positions(self.data['Raw Azimuth'], self.data['Raw Elevation'], new_bs)

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

    def run_track(self):
        modes = [self.data['Azimuth mode'], self.data['Elevation mode']]
        if modes[0] != 'ProgramTrack':
            return False
        # queue starts as empty set of 4 empty lists, and the number of free spaces (10000)
        queue = self.queue

        # initialize discard queue, used for cubic spline interpolation on
        # turnarounds
        discard_queue = {'times': [], 'azs': [], 'els': [], 'azflags': []}
        turnaround = False

        # work through 10 items on the stack at a time
        discard_num = 10
        # while there are more items in the queue than 10
        while len(queue['times']) > discard_num:
            # print('times: ' + str(len(queue['times'])))
            # print('azs: ' + str(len(queue['azs'])))
            # print('els: ' + str(len(queue['els'])))
            # print('flags: ' + str(len(queue['azflags'])))

            # grab front 10 flags, which signal an approaching turnaround
            next10flags = queue['azflags'][:10]
            turnaround = False
            if 2 in next10flags:
                turnaround = True

            if not turnaround:
                # interpolate between next 10 points, produces functions for az
                # and el
                fittimes = queue['times'][:10]
                fitazs = queue['azs'][:10]
                fitels = queue['els'][:10]
                azfit = interp1d(fittimes, fitazs, fill_value="extrapolate")
                elfit = interp1d(fittimes, fitels, fill_value="extrapolate")
                discard_num = 10
            else:
                # if we hit a turnaround look at last 10 points, and next 15
                # perform CubicSpline interpolation for turnaround
                fittimes = discard_queue['times'][-10:]
                for i in queue['times'][:15]:
                    fittimes.append(i)
                fitazs = discard_queue['azs'][-10:]
                for j in queue['azs'][:15]:
                    fitazs.append(j)
                fitels = discard_queue['els'][-10:]
                for k in queue['els'][:15]:
                    fitels.append(k)
                try:
                    azfit = CubicSpline(fittimes, fitazs)
                    elfit = CubicSpline(fittimes, fitels)
                except ValueError:
                    print('Error in CubicSpline computation')
                    print('TIMES:', fittimes)
                    print('AZ:', fitazs)
                    print('EL:', fitazs)
                    raise ValueError
                discard_num = 15

            # delete items from queue, but keep a record of them in case we hit
            # a turnaround
            for i in range(discard_num):
                discard_queue['times'].append(queue['times'].pop(0))
                discard_queue['azs'].append(queue['azs'].pop(0))
                discard_queue['els'].append(queue['els'].pop(0))
                discard_queue['azflags'].append(queue['azflags'].pop(0))
                queue['free'] += 1

            # wait until beginning of the 10 points we popped off the queue
            nowtime = self.data['Time_UDP']
            while nowtime < fittimes[0]:
                time.sleep(0.1)
                nowtime = self.data['Time_UDP']
            # print('nowtime: ' + str(nowtime))
            # print('fittimes[-1]: ' + str(fittimes[-1]))

            # before we reach the end of the times we popped off the queue,
            # apply our interpolation and update the self.data object's
            # positions and timestamps
            while nowtime < fittimes[-1]:
                try:
                    newaz = float(azfit(nowtime))
                    newel = float(elfit(nowtime))
                    # print('newaz: '+str(newaz))
                    self.update_positions(newaz, newel, self.data['Raw Boresight'])
                    self.update_timestamp()
                    nowtime = self.data['Time_UDP']
                except ValueError:
                    time.sleep(0.01)
                    nowtime = self.data['Time_UDP']

        print(f"4 QUEUE {self.queue}", flush=True)
        # uploads the last point 30 times with azflag = 1, I think to clear out the queue?
        final_stretch = self.queue
        landing = {'times': [], 'azs': [], 'els': [], 'azflags': []}
        for i in range(30):
            landing['times'].append(final_stretch['times'][-1] + 0.1)
            landing['azs'].append(final_stretch['azs'][-1])
            landing['els'].append(final_stretch['els'][-1])
            landing['azflags'].append(1)
        print("LANDING:", landing, flush=True)
        print(f"5 QUEUE {self.queue}", flush=True)  # 9995 points in queue
        # 5 QUEUE {'times': array([13962.435132, 13962.535332, 13962.635532, 13962.735733, 13962.835933]),
        #          'azs': array([20.801603, 20.601202, 20.400802, 20.200401, 20. ]),
        #          'els': array([35., 35., 35., 35., 35.]),
        #          'azflags': array([1., 1., 1., 1., 0.]),
        #          'free': 9995}
        final_stretch['times'].extend(landing['times'])
        final_stretch['azs'].extend(landing['azs'])
        final_stretch['els'].extend(landing['els'])
        final_stretch['azflags'].extend(landing['azflags'])
        azfit = interp1d(final_stretch['times'], final_stretch['azs'], fill_value="extrapolate")
        elfit = interp1d(final_stretch['times'], final_stretch['els'], fill_value="extrapolate")

        stop_time = final_stretch['times'][-1]  # save the last time before we delete it
        # delete items from the queue, don't need to keep record this time
        # note: this very briefly puts the queue size over 10k, but that gets
        # fixed on the next call to update_queue() when the queue is empty
        discard_num = len(final_stretch['times'])
        for i in range(discard_num):
            queue['times'].pop(0)
            queue['azs'].pop(0)
            queue['els'].pop(0)
            queue['azflags'].pop(0)
            queue['free'] += 1

        nowtime = self.data['Time_UDP']
        print(f"6 QUEUE {self.queue}", flush=True)
        while nowtime < stop_time:
            newaz = float(azfit(nowtime))
            newel = float(elfit(nowtime))
            self.update_positions(newaz, newel, self.data['Raw Boresight'])
            # time.sleep(0.0001)
            self.update_timestamp()
            nowtime = self.data['Time_UDP']
        print(f"7 QUEUE {self.queue}", flush=True)

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
