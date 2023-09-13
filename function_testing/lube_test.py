import soaculib as aculib
import soaculib.status_keys as status_keys
import time
import datetime
import calendar
import numpy as np

AXIS = 'AzEl'  # Az, El, Azel

if __name__ == '__main__':
    import util
    acu = util.get_acu()

    def start():
        x = acu.Command('DataSets.Lubrication',
                        f'Start {AXIS} Lubrication')
        print(x)
    def stop():
        x = acu.Command('DataSets.Lubrication',
                        'Stop Lubrication')
        print(x)
