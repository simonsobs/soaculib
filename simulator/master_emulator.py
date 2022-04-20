import numpy as np
import time
import datetime as dt
from scipy.interpolate import CubicSpline, interp1d
import server_keys as sk
import struct
import pickle
from flask import Flask, request, jsonify

TZ = dt.timezone.utc

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
    current_hms = ((now.hour)*60*60 + now.minute*60 + now.second + now.microsecond*1e-6)
    current_day_part = current_hms/(24*60*60)
    current_time = current_day_of_year + current_day_part
    return current_time, current_day_of_year, current_hms

class DataMaster:
    def __init__(self, dataset):
        self.data = {}
        self.queue = {'times':np.array([]), 'azs':np.array([]), 'els':np.array([]), 'azflags':np.array([])}
        self.queue['free'] = 10000-len(self.queue['times'])
        print('self.queue = ' + str(self.queue))
        for key, val in sk.status_fields[dataset].items():
            if val == int:
                self.data[key] = 0
            elif val == bool:
                self.data[key] = False
            elif val == str:
                self.data[key] = 'Stop'
            elif val == float:
                self.data[key] = 0.0
        init_now = dt.datetime.now(TZ)
        init_time, init_day, init_hms = find_day_of_year(init_now)
        self.data['Day'] = init_day
        self.data['Time_UDP'] = init_hms
        self.data['Year'] = init_now.year
        self.data['Time'] = init_time
        self.data['Azimuth current position'] = 90.
        self.data['Raw Azimuth'] = 90.
        self.data['Corrected Azimuth'] = 90.
        self.data['Elevation current position'] = 90.
        self.data['Raw Elevation'] = 90.
        self.data['Corrected Elevation'] = 90.
        self.data['Boresight current position'] = 10.
        self.data['Raw Boresight'] = 10.
        self.data['Corrected Boresight'] = 10.
    def update_timestamp(self, now):
        new_data = self.data
        nowtime, nowday, nowhms = find_day_of_year(now)
        new_data['Day'] = nowday
        new_data['Time_UDP'] = nowhms
        new_data['Year'] = now.year
        new_data['Time'] = nowtime
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
        current_time = self.data['Time_UDP'] + 5.
        initial_times = np.linspace(current_time - 5., current_time-0.01, num=10)
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
            aslope = (azs[i] - azs[i-1]) / (aztimes[i] - aztimes[i-1])
            azslopes.append(aslope)
        for j in range(1, len(els)):
            eslope = (els[j] - els[j-1]) / (eltimes[j] - eltimes[j-1])
            elslopes.append(eslope)

        azcurve = CubicSpline(aztimes, azs)
        elcurve = CubicSpline(eltimes, els)
        azslopecurve = CubicSpline(aztimes[1:], azslopes)
        elslopecurve = CubicSpline(eltimes[1:], elslopes)

        nowtimestamp = current_time
        while nowtimestamp < max(aztimes):
            self.update_timestamp(dt.datetime.now(TZ))
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
        self.update_timestamp(dt.datetime.now(TZ))
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
            self.update_timestamp(dt.datetime.now(TZ))
            self.update_positions(self.data['Raw Azimuth'], self.data['Raw Elevation'], float(bscurve(nowtimestamp)))
            nowtimestamp = self.data['Time_UDP']
        self.update_timestamp(dt.datetime.now(TZ))
        self.update_positions(self.data['Raw Azimuth'], self.data['Raw Elevation'], new_bs)

    def upload_track(self, lines):
        slines = lines.decode('utf-8')
        linelist = slines.split('\r\n')
        doys = []
        #dtimes = []
        udptimes = []
        azpts = []
        elpts = []
        azflags = []
        for line in linelist:
        #    print(line)
            if len(line):
                acutime = line.split(';')[0]
                doy = int(acutime.split(', ')[0])
                utime = acutime.split(', ')[1]
                hr = float(utime.split(':')[0])
                mn = float(utime.split(':')[1])
                sc = float(utime.split(':')[2])
                azpt = float(line.split(';')[1])
                elpt = float(line.split(';')[2])
                azflag = int(line.split(';')[5])
                timeudp = hr*60.*60. + mn*60. + sc
                doys.append(doy)
                udptimes.append(timeudp)
                azpts.append(azpt)
                elpts.append(elpt)
                azflags.append(azflag)
       # print(self.queue)
#        print('udptimes len: '+str(len(udptimes)))
#        print('azflags len: ' + str(len(azflags)))
#        for i in range(len(udptimes)):
#            self.queue['times'].append(udptimes[i])
#            self.queue['azs'].append(azpts[i])
#            self.queue['els'].append(elpts[i])
#            self.queue['azflags'].append(azflags[i])
        self.queue['times'] = np.concatenate((self.queue['times'], udptimes))
        self.queue['azs'] = np.concatenate((self.queue['azs'], azpts))
        self.queue['els'] = np.concatenate((self.queue['els'], elpts))
        self.queue['azflags'] = np.concatenate((self.queue['azflags'], azflags))
        self.queue['free'] = 10000 - len(self.queue['times'])
        self.update_data('Qty of free program track stack positions', self.queue['free'])
        print(len(self.queue['times']))
        print(len(self.queue['azs']))
        print(len(self.queue['els']))
        print(len(self.queue['azflags']))

    def run_track(self):
        modes = [self.data['Azimuth mode'], self.data['Elevation mode']]
        if modes[0] != 'ProgramTrack':
            return False
        queue = self.queue
     #   print(queue)
        discard_queue = {'times':[], 'azs':[], 'els':[], 'azflags':[]}
        turnaround = False
        discard_num = 10
        while len(queue['times'])>discard_num:
 #           print('times: ' + str(len(queue['times'])))
 #           print('azs: ' + str(len(queue['azs'])))
 #           print('els: ' + str(len(queue['els'])))
 #           print('flags: ' + str(len(queue['azflags'])))
            next10flags = queue['azflags'][:10]
            if 2 in next10flags:
                turnaround = True
            else:
                turnaround = False
            if turnaround:
                fittimes = discard_queue['times'][-10:]
                for i in queue['times'][:15]:
                    fittimes.append(i)
                fitazs = discard_queue['azs'][-10:]
                for j in queue['azs'][:15]:
                    fitazs.append(j)
                fitels = discard_queue['els'][-10:]
                for k in queue['els'][:15]:
                    fitels.append(k)
                azfit = CubicSpline(fittimes, fitazs)
                elfit = CubicSpline(fittimes, fitels)
                discard_num = 15 
            else:
                fittimes = queue['times'][:10]
                fitazs = queue['azs'][:10]
                fitels = queue['els'][:10]
                azfit = interp1d(fittimes, fitazs)
                elfit = interp1d(fittimes, fitels)
                discard_num = 10
            for i in range(discard_num):
                discard_t = self.queue['times'][0]#self.queue['times'].pop(0)
                discard_az = self.queue['azs'][0]#self.queue['azs'].pop(0)
                discard_el = self.queue['els'][0]#self.queue['els'].pop(0)
                discard_flag = self.queue['azflags'][0]#self.queue['azflags'].pop(0)
                self.queue['times'] = np.delete(self.queue['times'], 0)
                self.queue['azs'] = np.delete(self.queue['azs'], 0)
                self.queue['els'] = np.delete(self.queue['els'], 0)
                self.queue['azflags'] = np.delete(self.queue['azflags'], 0)
                self.queue['free'] += 1
                discard_queue['times'].append(discard_t)
                discard_queue['azs'].append(discard_az)
                discard_queue['els'].append(discard_el)
                discard_queue['azflags'].append(discard_flag)
            nowtime = self.data['Time_UDP']
     #       while nowtime < fittimes[0]:
     #           time.sleep(0.01)
     #           nowtime = self.data['Time_UDP']
  #          print('nowtime: ' + str(nowtime))
  #          print('fittimes[-1]: ' + str(fittimes[-1]))
            while nowtime < fittimes[0]:
                time.sleep(0.1)
                nowtime = self.data['Time_UDP']
            while nowtime < fittimes[-1]:
                try:
                    newaz = float(azfit(nowtime))
                    newel = float(elfit(nowtime))
   #                 print('newaz: '+str(newaz))
                    self.update_positions(newaz, newel, self.data['Raw Boresight'])
                    self.update_timestamp(dt.datetime.now(TZ))
                    nowtime = self.data['Time_UDP']
                except ValueError:
                    time.sleep(0.01)
                    nowtime = self.data['Time_UDP']
            queue = self.queue
      #      print(queue)
        final_stretch = self.queue
        landing = {'times':[], 'azs':[], 'els':[], 'azflags':[]}
        for i in range(30):
            landing['times'].append(final_stretch['times'][-1]+0.1)
            landing['azs'].append(final_stretch['azs'][-1])
            landing['els'].append(final_stretch['els'][-1])
            landing['azflags'].append(1)
        final_stretch['times'] = np.concatenate((final_stretch['times'], landing['times']))
        final_stretch['azs'] = np.concatenate((final_stretch['azs'], landing['azs']))
        final_stretch['els'] = np.concatenate((final_stretch['els'], landing['els']))
        final_stretch['azflags'] = np.concatenate((final_stretch['azflags'], landing['azflags']))
        azfit = interp1d(final_stretch['times'], final_stretch['azs'])
        elfit = interp1d(final_stretch['times'], final_stretch['els'])
        nowtime = self.data['Time_UDP']
        while nowtime < final_stretch['times'][-1]:
            newaz = float(azfit(nowtime))
            newel = float(elfit(nowtime))
            self.update_positions(newaz, newel, self.data['Raw Boresight'])
     #       time.sleep(0.0001)
            self.update_timestamp(dt.datetime.now(TZ))
            nowtime = self.data['Time_UDP']
        return True

    def values(self):
        self.update_timestamp(dt.datetime.now(TZ))
        return self.data


app = Flask(__name__)
satp = DataMaster('Datasets.StatusSATPDetailed8100')

@app.route("/Values", methods=["GET"])
def get_data():
    data = satp.values()
    identifier = request.form.get('identifier')
    form = request.args.get('format')
    if identifier == 'DataSets.StatusSATPDetailed8100':
        if form == 'JSON':
            return jsonify(data)
        else:
            return jsonify(data)
    else:
        return jsonify(data)

@app.route("/Version", methods=["GET"])
def get_version():
    version = 'Simulator Version 1.0'
    return version

@app.route("/Command", methods=["GET"])
def command():
    identifier = request.args.get('identifier')
    cmd = request.args.get('command')
    param = request.args.get('parameter')    
    if identifier == "DataSets.CmdAzElPositionTransfer":
        if cmd == 'Set Azimuth Elevation':
            azel = param.split('|')
            az = float(azel[0])
            el = float(azel[1])
            satp.preset_azel_motion(az, el)
        else:
            return 'command not found'
    elif identifier == "DataSets.CmdTimePositionTransfer":
        if cmd == "Clear Stack":
            satp.queue = {'times':np.array([]), 'azs':np.array([]), 'els':np.array([]), 'azflags':np.array([]), 'free':10000}
            satp.update_data('Qty of free program track stack positions', satp.queue['free'])
        else:
            return 'command not found'
    elif identifier == "DataSets.CmdModeTransfer":
        if cmd == "Set3rdAxisMode":
            new_mode = param
            satp.change_mode(axes=['Boresight'], modes=[new_mode])
        elif cmd == "SetAzElMode":
            satp.change_mode(axes=['Azimuth', 'Elevation'], modes=[param, param])
        elif cmd == "SetModes":
            new_azmode = param[0]
            new_elmode = param[1]
            satp.change_mode(axes=['Azimuth', 'Elevation'], modes=[new_azmode, new_elmode])
        else:
            return 'command not found'
    elif identifier == "DataSets.Cmd3rdAxisPositionTransfer":
        new_bs = float(param)
        satp.preset_bs_motion(new_bs)
    else:
        return 'identifier not found'
    data = satp.values()
    return 'ok, command executed'

@app.route("/UploadPtStack", methods=["POST"])
def upload():
    upload_lines = request.data
    satp.upload_track(upload_lines)
    satp.run_track()
    return 'ok, command executed'

if __name__ == "__main__":
    app.run(host="localhost", port=8102, debug=False)#, threaded=False, processes=3)
