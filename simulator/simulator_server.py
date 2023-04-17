import numpy as np
from threading import Thread
from flask import Flask, request, jsonify

from master_emulator import DataMaster
from udp_server import AcuUdpServer

satp = DataMaster('Datasets.StatusSATPDetailed8100')
udp = AcuUdpServer(10008, satp)
app = Flask(__name__)

# Useful for turning off Flask logs
# import logging
# log = logging.getLogger('werkzeug')
# log.disabled = True


@app.route("/Values", methods=["GET"])
def get_data():
    data = satp.values()
    identifier = request.args.get('identifier')
    form = request.args.get('format')
    if identifier == 'DataSets.StatusSATPDetailed8100':
        if form == 'JSON':
            return jsonify(data)
        else:
            return jsonify(data)
    elif identifier.split('.')[1] == 'SkyAxes':
        SkyAxes = {'Azimuth': {'Mode': data['Azimuth mode']},
                   'Elevation': {'Mode': data['Elevation mode']},
                   'Boresight': {'Mode': data['Boresight mode']}}
        axis = identifier.split('.')[2]
        return jsonify(SkyAxes[axis])
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
        elif cmd =='Set Azimuth':
            az = float(param)
            satp.preset_azel_motion(new_az=az)
        elif cmd =='Set Elevation':
            el = float(param)
            satp.preset_azel_motion(new_el=el)
        else:
            return 'command not found'
    elif identifier == "DataSets.CmdTimePositionTransfer":
        if cmd == "Clear Stack":
            satp.clear_queue()
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
            param = param.split('|')
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
    satp.values()
    return 'OK, Command executed.'


@app.route("/UploadPtStack", methods=["POST"])
def upload():
    upload_lines = request.data
    satp.upload_track(upload_lines)

    # call run_track() in thread so we can continue to upload points
    if not satp.running:
        motion_thread = Thread(target=satp.run_track)
        motion_thread.start()

    return 'ok, command executed'


if __name__ == "__main__":
    # start background thread updating internal ACU data
    satp.run()

    flask_kwargs = {'host': 'localhost', 'port': 8102, 'debug': False}
    #flask_kwargs = {'host': 'localhost', 'port': 8102, 'debug': False, 'threaded': False, 'processes': 3}
    t1 = Thread(target=app.run, kwargs=flask_kwargs)
    t2 = Thread(target=udp.run)

    t1.start()
    t2.start()
