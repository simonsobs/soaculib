# Fans can be set on / off and also the target speed can be set to
# 40-100.  Fans pull air in from outside.  Boosters are for internal
# circulation of a space and can be set to on/off only.
#
# There is a "Traverse" temperature setpoint as well but at the time
# of this writing is doesn't do anything.
#

import soaculib as aculib
import time
import sys

fans = [
    'Fan EL Housing',
    'Fan Yoke Arm B',
    'Fan Yoke Arm A Instrument Space',
    'Fan Yoke Traverse B Process Space',
    'Fan Yoke Traverse M Servo Space',
    'Fan Yoke Traverse A Electronic Space',
]
boosters = [
    'Booster EL Housing',
    'Booster Yoke Traverse B Process Space',
    'Booster Yoke Traverse M Servo Space',
    'Booster Yoke Traverse A Electronic Space',
]


if __name__ == '__main__':
    import util
    acu = util.get_acu()

    target = None
    if len(sys.argv) > 1:
        target = sys.argv[1]

    def start():
        x = acu.Command('DataSets.HVAC',
                        f'switch on {target}')
        print(x)
        time.sleep(2)
        probe()
    def stop():
        x = acu.Command('DataSets.HVAC',
                        f'switch off {target}')
        print(x)
        time.sleep(2)
        probe()
    def speed(sp):
        assert (target in fans)
        x = acu.Command('DataSets.HVAC',
                        f'set speed {target}', sp)
        print(x)
        time.sleep(2)
        probe()

    def probe():
        data = acu.Values('DataSets.HVAC')
        for k in data:
            if target in k:
                print(k, data[k])

    def check_status():
        data = acu.Values('DataSets.HVAC')
        print('Fans')
        for f in fans:
            print(f)
            for k in [f'{f} on', f'{f} Failure', f'Setpoint Speed {f}']:
                msg = 'ok' if k in data else 'MISSING'
                print(f'  {msg:<8}:  {k}')

        print()
        print('Boosters')
        for f in boosters:
            print(f)
            for k in [f'{f} on', f'{f} Failure']:
                msg = 'ok' if k in data else 'MISSING'
                print(f'  {msg:<8}:  {k}')
        print()

        return data

    def set_temp_setpoint(t):
        # 15 - 20 C
        x = acu.Command('DataSets.HVAC',
                        'Set temperature Yoke Traverse',
                        t)
        print(x)

    def test_fans():
        for target in fans:
            print(target)
            probe()
