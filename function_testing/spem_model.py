import numpy as np
from numpy import cos, sin, tan

DEG = np.pi/180

def delta(az_el, params, vel=0):
    class _noisyzerodict(dict):
        warned = []
        def __getitem__(self, key):
            try:
                return super().__getitem__(key)
            except KeyError:
                if key not in self.warned:
                    print('Warning, %s not found.' % key)
                    self.warned.append(key)
            return 0.

    params = _noisyzerodict(params)

    az, el = az_el[0] * DEG, az_el[1] * DEG
    delta_az, delta_el = 0., 0.
    # 2.3.2
    delta_az += params['IA']
    delta_el += params['IE']
    # 2.3.3
    if el <= np.pi / 2:
        delta_el += params['TF'] * cos(el) + params['TFS'] * sin(el)
        delta_el += params['TFC']
    else:
        # Confirmed this sign.
        delta_el += -params['TFE'] * cos(el) + params['TFES'] * sin(el)
        delta_el += params['TFEC']

    # 2.3.4
    delta_az += (
        - params['AN'] * tan(el) * sin(az) +
        - params['AW'] * tan(el) * cos(az) +
        - params['AN2'] * tan(el) * sin(2*az) +
        - params['AW2'] * tan(el) * cos(2*az))
    delta_el += (
        - params['AN'] * cos(az) +
        + params['AW'] * sin(az) +
        - params['AN2'] * cos(2*az) +
        + params['AW2'] * sin(2*az))
    # 2.3.5
    delta_az += -params['NPAE'] * tan(el)
    # 2.3.6
    delta_az += -params['CA'] / cos(el)
    # 2.3.7
    delta_az += (
        params['AES'] * sin(az) +
        params['AEC'] * cos(az) +
        params['AES2'] * sin(2*az) +
        params['AEC2'] * cos(2*az))
    delta_el += (
        params['EES'] * sin(el) +
        params['EEC'] * cos(el) +
        params['EES2'] * sin(2*el) +
        params['EEC2'] * cos(2*el))
    # 2.3.8 - present in LAT on Sep 18 2023
    delta_az += (
        - params['NRX'] +
        - params['NRY'] * tan(el))
    ## Note sign difference here relative to ICD!
    delta_el += (
        - params['NRX'] * sin(el) +
        + params['NRY'] * cos(el))

    # 2.3.9 - "Beam Squint", CRX and CRY; not impl.

    # No ICD for LELA, LELE.  These terms are both proportional to
    # elevation velocity, account for the fact that the drive is on
    # one side of the axis and that can lead to some flexure.
    if abs(vel) > params['velocity']:  #mostly for the velocity=0 case
        scalar = 1.
    else:
        scalar = abs(vel) / params['velocity']

    delta_az += \
        params['LELA'] * np.sign(vel) / cos(el) * scalar
    delta_el +=  \
        params['LELE'] * np.sign(vel) * scalar

    return np.array([delta_az, delta_el])

