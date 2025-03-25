import time
import os
import logging
import numpy as np
from threading import Thread
from flask import Flask, request, jsonify

from master_emulator import DataMaster
from udp_server import AcuUdpServer

satp = DataMaster('Datasets.StatusSATPDetailed8100')
udp = AcuUdpServer(10008, satp)
app = Flask(__name__)


@app.route("/Values", methods=["GET"])
def get_data():
    identifier = request.args.get('identifier')
    form = request.args.get('format')
    assert form == 'JSON'

    data = {
        'Not Implemented': identifier
    }

    tokens = identifier.lower().split('.')
    if tokens[0] == 'datasets':
        if tokens[1] == 'StatusSATPDetailed8100'.lower():
            data = satp.values()
            return jsonify(data)
        elif tokens[1] == 'Shutter'.lower():
            data = {
                # ACU dataset has a timestamp too...
                'Shutter Closed' : False,
                'Shutter Moving' : False,
                'Shutter Open' : True,
                'Shutter Timeout' : False,
                'Shutter Failure' : False,
                'Move Interlock' : False,
            }

    elif tokens[:2] == ['antenna', 'skyaxes']:
        data = satp.values()
        SkyAxes = {'azimuth': {'Mode': data['Azimuth mode']},
                   'elevation': {'Mode': data['Elevation mode']},
                   'boresight': {'Mode': data['Boresight mode']},  # deprecated
                   'polarisation': {'Mode': data['Boresight mode']}}
        axis = tokens[2]
        data = SkyAxes[axis]

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
        all_axes = ['Azimuth', 'Elevation', 'Boresight']
        if cmd == "Set3rdAxisMode":
            new_mode = param
            satp.change_mode(axes=['Boresight'], modes=[new_mode])
        elif cmd == "SetAzElMode":
            satp.change_mode(axes=['Azimuth', 'Elevation'], modes=[param, param])
        elif cmd == "SetModes":
            param = param.split('|')  # Could be 2 or 3 params.
            axes, modes = zip(*zip(all_axes, param))
            satp.change_mode(axes=axes, modes=modes)
        elif cmd == 'Stop':
            satp.change_mode(axes=all_axes, modes=['Stop'] * len(all_axes))
        else:
            return 'command not found'
    elif identifier == "DataSets.Cmd3rdAxisPositionTransfer":
        new_bs = float(param)
        satp.preset_bs_motion(new_bs)
    elif identifier == "DataSets.Shutter":
        assert cmd in ['ShutterOpen', 'ShutterClose']
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
    flask_logs = os.getenv('ACUSIM_FLASK_LOG') not in [None, '', '0']
    if not flask_logs:
        log = logging.getLogger('werkzeug')
        log.disabled = True

    port = int(os.getenv('ACUSIM_HTTP_PORT', 8102))

    # start background thread updating internal ACU data
    satp.run()

    flask_kwargs = {'host': 'localhost', 'port': port, 'debug': False}
    t1 = Thread(target=app.run, kwargs=flask_kwargs)
    t2 = Thread(target=udp.run)

    t1.start()
    t2.start()
