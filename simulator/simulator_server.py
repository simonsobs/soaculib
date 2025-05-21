import time
import os
import logging
import numpy as np
from threading import Thread
from flask import Flask, request, jsonify

from master_emulator import DataMaster, initialize_data_dict
from udp_server import AcuUdpServer

app = Flask(__name__)

# Simulator globals, updated in main.
pconfig = {}
pdata = None
udp = None


# Stuff my ACU says.
OK_RESPONSES = {
    'exec': 'OK, Command executed.',
    'send': 'OK, Command send.',
}


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
        if tokens[1] == pconfig['status'].lower():
            data = pdata.values()
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
        elif tokens[1] == 'StatusDetailed8100_3rd'.lower():
            # The LAT co-rotator dataset -- make it look normal but
            # then copy in some "Boresight" state from pdata...
            vals = pdata.values()
            data = initialize_data_dict(
                'DataSets.StatusDetailed8100_3rd', set_defaults=False)
            for k in [
                    'current position',
                    'brakes released',
                    'mode',
                    'commanded position',
            ]:
                data[f'Co-Rotator {k}'] = vals[f'Boresight {k}']
            return data
    elif tokens[:2] == ['antenna', 'skyaxes']:
        data = pdata.values()
        SkyAxes = {'azimuth': {'Mode': data['Azimuth mode']},
                   'elevation': {'Mode': data['Elevation mode']},
                   # The boresight mode (SATP) / corotator mode (LAT)
                   # are queried throught the common axis
                   # "Polarisation".
                   'polarisation': {'Mode': data['Boresight mode']},
                   }
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
    ok_val = OK_RESPONSES['exec']

    if identifier == "DataSets.CmdAzElPositionTransfer":
        if cmd == 'Set Azimuth Elevation':
            azel = param.split('|')
            az = float(azel[0])
            el = float(azel[1])
            pdata.preset_azel_motion(az, el)
        elif cmd =='Set Azimuth':
            az = float(param)
            pdata.preset_azel_motion(new_az=az)
        elif cmd =='Set Elevation':
            el = float(param)
            pdata.preset_azel_motion(new_el=el)
        else:
            return 'command not found'
    elif identifier == "DataSets.CmdTimePositionTransfer":
        if cmd == "Clear Stack":
            pdata.clear_queue()
            pdata.update_data('Qty of free program track stack positions', pdata.queue['free'])
        elif cmd in [
                "Set Profiler On",
                "Set Profiler Off",
                "Set Interpolation Linear",
                "Set Interpolation Spline",
        ]:
            pass  # sure, whatever.
        else:
            return 'command not found'
    elif identifier == "DataSets.CmdModeTransfer":
        all_axes = ['Azimuth', 'Elevation', 'Boresight']
        if cmd == "Set3rdAxisMode":
            new_mode = param
            pdata.change_mode(axes=['Boresight'], modes=[new_mode])
        elif cmd == "SetAzElMode":
            pdata.change_mode(axes=['Azimuth', 'Elevation'], modes=[param, param])
        elif cmd == "SetModes":
            param = param.split('|')  # Could be 2 or 3 params.
            axes, modes = zip(*zip(all_axes, param))
            pdata.change_mode(axes=axes, modes=modes)
            ok_val = OK_RESPONSES['send']
        elif cmd == 'Stop':
            pdata.change_mode(axes=all_axes, modes=['Stop'] * len(all_axes))
        else:
            return 'command not found'
    elif identifier == "DataSets.Cmd3rdAxisPositionTransfer":
        new_bs = float(param)
        pdata.preset_bs_motion(new_bs)
    elif identifier == "DataSets.Shutter":
        assert cmd in ['ShutterOpen', 'ShutterClose']
    else:
        return 'identifier not found'
    pdata.values()
    return ok_val


@app.route("/UploadPtStack", methods=["POST"])
def upload():
    upload_lines = request.data
    pdata.upload_track(upload_lines)

    # call run_track() in thread so we can continue to upload points
    if not pdata.running:
        motion_thread = Thread(target=pdata.run_track)
        motion_thread.start()

    return 'ok, command executed'


if __name__ == "__main__":
    flask_logs = os.getenv('ACUSIM_FLASK_LOG') not in [None, '', '0']
    if not flask_logs:
        log = logging.getLogger('werkzeug')
        log.disabled = True

    port = int(os.getenv('ACUSIM_HTTP_PORT', 8102))
    udp_port = int(os.getenv('ACUSIM_HTTP_BROADCAST_PORT', 10008))

    platform = os.getenv('ACUSIM_PLATFORM', 'satp')
    if platform in ['satp', '', None]:
        platform = 'satp'
        pconfig['status'] = 'StatusSATPDetailed8100'
    elif platform in 'ccat':
        pconfig['status'] = 'StatusCCATDetailed8100'
    else:
        raise ValueError(f'Invalid ACUSIM_PLATFORM: {platform}')

    # Note that regardless of name from which it is served, we init it
    # from the SATP one...
    pdata = DataMaster('Datasets.StatusSATPDetailed8100')
    udp = AcuUdpServer(udp_port, pdata)

    # start background thread updating internal ACU data
    pdata.run()

    flask_kwargs = {'host': 'localhost', 'port': port, 'debug': False}
    t1 = Thread(target=app.run, kwargs=flask_kwargs)
    t2 = Thread(target=udp.run)

    t1.start()
    t2.start()
