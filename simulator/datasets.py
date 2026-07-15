import time
import random


# Use these generators to create some random variation.

def var_normal(mean=0., sigma=1., timescale=0.):
    return _randomize(timescale,
                      random.normalvariate,
                      (mean, sigma))


def var_bool(truthiness=0.5, timescale=0.):
    def onoff():
        return (random.random() <= truthiness)
    return _randomize(timescale, onoff)


def _randomize(timescale, func, args=(), kwargs={}):
    last_time = None
    while True:
        now = time.time()
        if last_time is None or (now - last_time) >= timescale:
            last_val = func(*args, **kwargs)
            last_time = now
        yield last_val


datasets = {
    'hvac': {  # "DataSets.HVAC"
        #"Time": 212.06530052088,
        #"Year": 2025,
        "Temperature EL Housing 1": -7.5,
        "Temperature EL Housing 2": -7.5,
        "Temperature EL Housing 3": -7.6,
        "Temperature EL Housing 4": -7.4,
        "Temperature EL Housing 5": -7.6,
        "Temperature EL Housing 6": -7.5,
        "Temperature Yoke Arm B 1": var_normal(-5, 1.),
        "Temperature Yoke Arm B 2": -5.1,
        "Temperature Yoke Arm B 3": -5.1,
        "Temperature Yoke Arm B 4": -4.5,
        "Temperature Yoke Arm A Instrument Space 1": 0.3,
        "Temperature Yoke Arm A Instrument Space 2": -2.7,
        "Temperature Yoke Arm A Instrument Space 3": 0.5,
        "Temperature Yoke Arm A Instrument Space 4": -3.1,
        "Temperature Yoke Arm A Instrument Space 5": -2.6,
        "Temperature Yoke Arm A Instrument Space 6": -0.9,
        "Temperature Yoke Traverse B Process Space 1": 1.0,
        "Temperature Yoke Traverse B Process Space 2": 2.9,
        "Temperature Yoke Traverse B Process Space 3": 1.8,
        "Temperature Yoke Traverse B Process Space 4": 1.3,
        "Temperature Yoke Traverse M Servo Space 1": 4.7,
        "Temperature Yoke Traverse M Servo Space 2": 6.0,
        "Temperature Yoke Traverse M Servo Space 3": 4.4,
        "Temperature Yoke Traverse M Servo Space 4": 2.3,
        "Temperature Yoke Traverse A Electronic Space 1": 6.9,
        "Temperature Yoke Traverse A Electronic Space 2": 3.9,
        "Temperature Yoke Traverse A Electronic Space 3": 3.3,
        "Temperature Yoke Traverse A Electronic Space 4": 5.6,
        "Temperature MPD Container 1": 5.4,
        "Temperature MPD Container 2": 6.3,
        "Temperature Ambient 1": -7.7,
        "Temperature Ambient 2": -7.6,
        "Temperature Average EL Housing": -7.51,
        "Temperature Average Yoke Arm B": -4.97,
        "Temperature Average Yoke Arm A Instrument Space": -1.41,
        "Temperature Average Yoke Traverse B Process Space": 1.75,
        "Temperature Average Yoke Traverse M Servo Space": 4.35,
        "Temperature Average Yoke Traverse A Electronic Space": 4.92,
        "Temperature Average MPD Container": 5.85,
        "Temperature Average Ambient": -7.65,
        "Setpoint Temperature Yoke Traverse": 13.0,
        "Setpoint Speed Fan Yoke Arm B": 95,
        "Setpoint Speed Fan Yoke Arm A Instrument Space": 97,
        "Setpoint Speed Fan Yoke Traverse B Process Space": 67,
        "Setpoint Speed Fan Yoke Traverse M Servo Space": 95,
        "Setpoint Speed Fan Yoke Traverse A Electronic Space": 58,
        "Booster EL Housing Failure": False,
        "Booster Yoke Traverse B Process Space Failure": False,
        "Booster Yoke Traverse M Servo Space Failure": False,
        "Booster Yoke Traverse A Electronic Space Failure": False,
        "Fan EL Housing Failure": False,
        "Fan Yoke Arm B Failure": var_bool(),
        "Fan Yoke Arm A Instrument Space Failure": False,
        "Fan Yoke Traverse B Process Space Failure": False,
        "Fan Yoke Traverse M Servo Space Failure": False,
        "Fan Yoke Traverse A Electronic Space Failure": False,
        "Booster EL Housing on": False,
        "Booster Yoke Traverse B Process Space on": False,
        "Booster Yoke Traverse M Servo Space on": False,
        "Booster Yoke Traverse A Electronic Space on": False,
        "Fan EL Housing on": False,
        "Fan Yoke Arm B on": False,
        "Fan Yoke Arm A Instrument Space on": var_bool(),
        "Fan Yoke Traverse B Process Space on": False,
        "Fan Yoke Traverse M Servo Space on": False,
        "Fan Yoke Traverse A Electronic Space on": False,
        "Heater on": False,
    },
    'powerdistribution':
    {
        'Q2006 DAPS 1': True,
        'Q2007 DAPS 2': False,
        'Q2008 DAPS 3': True,
        'Q2009 DAPS 4': False,
        'Q2010 DAPS 5': True,
        'Q2011 DAPS 6': False,
        'Q2012 DAPS 7': True,
        'Q2013 DAPS 8': False,
        'Main Lighting': True,
        'Lights 42 Process Space': False,
        'Lights 44 Electronic Space': False,
        'Lights 45 Instrument Space 1': False,
        'Lights 46 Instrument Space 2': False,
    },
}
