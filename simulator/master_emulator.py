import numpy as np
import time
import datetime as dt
from scipy.interpolate import CubicSpline
import server_keys as sk
import struct
import pickle
from flask import Flask, request, jsonify

def find_day_of_year(now):
    """
    Function to find the current day of the year.

    Input: now (datetime object, datetime.datetime.now())

    Returns: current time as a portion of a day of the year
    """
    months = {1:31, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
    year = now.year
    if year % 4 == 0:
        months[2] = 29
    else:
        months[2] = 28
    current_day_of_year = 0
    for i in range(1, now.month):
        current_day_of_year += months[i]
    current_day_of_year += now.day
    current_hms = (now.hour*60*60 + now.minute*60 + now.second + now.microsecond*1e-6)
    current_day_part = current_hms/(24*60*60)
    current_time = current_day_of_year + current_day_part
    return current_time, current_day_of_year, current_hms

class DataMaster:
    def __init__(self, dataset):
        self.data = {}
        for key, val in sk.status_fields[dataset].items():
            if val == int:
                self.data[key] = 0
            elif val == bool:
                self.data[key] = False
            elif val == str:
                self.data[key] = 'Stop'
            elif val == float:
                self.data[key] = 0.0
        init_now = dt.datetime.now()
        init_time, init_day, init_hms = find_day_of_year(init_now)
        self.data['Day'] = init_day
        self.data['Time_UDP'] = init_hms
        self.data['Year'] = init_now.year
        self.data['Time_Status'] = init_time
        self.data['Azimuth current position'] = 90.
        self.data['Raw Azimuth'] = 90.
        self.data['Corrected Azimuth'] = 90.
        self.data['Elevation current position'] = 90.
        self.data['Raw Elevation'] = 90.
        self.data['Corrected Elevation'] = 90.
        self.data['Boresight current position'] = 10.
        self.data['Raw Boresight'] = 10.
        self.data['Corrected Elevation'] = 10.
    def update_timestamp(self, now):
        new_data = self.data
        nowtime, nowday, nowhms = find_day_of_year(now)
        new_data['Day'] = nowday
        new_data['Time_UDP'] = nowhms
        new_data['Year'] = now.year
        new_data['Time_Status'] = nowtime
        self.data = new_data
    def update_positions(self, new_az, new_el, new_bs):
        new_data = self.data
        new_data['Azimuth current position'] = new_az
        new_data['Raw Azimuth'] = new_az
        new_data['Corrected Azimuth'] = new_az
        new_data['Elevation current position'] = new_el
        new_data['Raw Elevation'] = new_el
        new_data['Corrected Elevation'] = new_el
        new_data['Boresight current position'] = new_bs
        new_data['Raw Boresight'] = new_bs
        new_data['Corrected Boresight'] = new_bs
        self.data = new_data
    def update_data(self, key, new_value):
        new_data = self.data
        new_data[key] = new_value
        self.data = new_data
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
        current_time = self.data['Time_UDP'] + 1.
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
            for ix in missintime_ixs:
                aztimes = np.append(aztimes, eltimes[ix])
                azs = np.append(azs, new_az)
        else:
            pass

        azslopes = []
        elslopes = []
        for i in range(1, len(azs)):
            aslope = (azs[i] - azs[i-1]) / (aztimes[i] - aztimes[i-1])
            azslopes.append(aslope)
        for j in range(1, len(els)):
            eslope = (els[i] - els[i-1]) / (eltimes[i] - eltimes[i-1])
            elslopes.append(eslope)

        azcurve = CubicSpline(aztimes, azs)
        elcurve = CubicSpline(eltimes, els)
        azslopecurve = CubicSpline(aztimes[1:], azslopes)
        elslopecurve = CubicSpline(eltimes[1:], elslopes)

        nowtimestamp = current_time
        while nowtimestamp < max(aztimes):
            self.update_timestamp(dt.datetime.now())
            input_az = float(azcurve(nowtimestamp))
            input_el = float(elcurve(nowtimestamp))
            self.update_positions(input_az, input_el, self.data['Raw Boresight'])
            if azvel > 0:
                self.update_data('Azimuth Current 1', 3 + 0.1*np.random.random())
                self.update_data('Azimuth Current 2', 3 + 0.1*np.random.random())
            if azvel < 0:
                self.update_data('Azimuth Current 1', -1*(3+0.1*np.random.random()))
                self.update_data('Azimuth Current 2', -1*(3+0.1*np.random.random()))
            if elvel > 0:
                self.update_data('Elevation Current 1', (3+0.1*np.random.random()))
            if elvel < 0:
                self.update_data('Elevation Current 1', -1*(3+0.1*np.random.random()))
            if nowtimestamp == current_time:
                self.update_data('Azimuth current velocity', azvel)
                self.update_data('Elevation current velocity', elvel)
            elif nowtimestamp != current_time:
                self.update_data('Azimuth current velocity', float(azslopecurve(nowtimestamp)))
                self.update_data('Elevation current velocity', float(elslopecurve(nowtimestamp)))
            time.sleep(0.001)
            nowtimestamp = self.data['Time_UDP']
        self.update_timestamp(dt.datetime.now())
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
        new_data = self.data
        for i in range(len(axes)):
            new_data[axes[i]+" mode"] = modes[i]
        self.data = new_data
        
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
            self.update_timestamp(dt.datetime.now())
            self.update_positions(self.data['Raw Azimuth'], self.data['Raw Elevation'], float(bscurve(nowtimestamp)))
            nowtimestamp = self.data['Time_UDP']
        self.update_timestamp(dt.datetime.now())
        self.update_positions(self.data['Raw Azimuth'], self.data['Raw Elevation'], new_bs)

    def upload_track(self, lines):
        pass

    def values(self):
        self.update_timestamp(dt.datetime.now())
        return self.data


app = Flask(__name__)
satp = DataMaster('Datasets.StatusSATPDetailed8100')

@app.route("/Values", methods=["GET"])
def get_data():
    data = satp.values()
    return jsonify(data)

@app.route("/Command", methods=["GET", "POST"])
def command():
    identifier = request.form.get('identifier')
    cmd = request.form.get('command')
    param = request.form.get('parameter')
    if identifier == "DataSets.CmdAzElPositionTransfer":
        c = cmd.split(' ')[0]
        ax1 = cmd.split(' ')[1]
        ax2 = cmd.split(' ')[2]
        azel = param.strip(' ').strip('[').strip(']').split(',')
        az = float(azel[0])
        el = float(azel[1])
        tt = satp.preset_azel_motion(az, el)
        return str(tt)
    elif identifier == "DataSets.CmdModeTransfer":
        if cmd == "Set3rdAxisMode":
            new_mode = param
            satp.change_mode(axes=['Boresight'], modes=[new_mode])
        elif cmd == "SetAzElMode":
            new_modes = []
            for i in param.split("'"):
                if len(i) > 2:
                    new_modes.append(i)
            new_azmode = new_modes[0]
            new_elmode = new_modes[1]
            satp.change_mode(axes=['Azimuth', 'Elevation'], modes=[new_azmode, new_elmode])
#            satp.data['Azimuth mode'] = new_azmode
#            satp.data['Elevation mode'] = new_elmode
    elif identifier == "DataSets.Cmd3rdAxisPositionTransfer":
        new_bs = float(param)
        satp.preset_bs_motion(new_bs)
    else:
        return 'identifier not found'
    data = satp.values()
    return 'ok, command executed'

@app.route("/UploadPtStack", methods=["POST"])
def upload():
    Type = request.form.get('Type')
    filename = request.form.get('filename')
    return(Type, filename)

if __name__ == "__main__":
    app.run(host="localhost", port=8102, debug=False, threaded=False, processes=3)
