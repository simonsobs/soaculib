import soaculib as aculib
import soaculib.status_keys as status_keys
import time
import datetime
import calendar
import numpy as np

def timecode(acutime):
    """
    Takes the time code produced by the ACU status stream and returns
    a ctime.

    Args:
        acutime (float): The time recorded by the ACU status stream,
                         corresponding to the fractional day of the year
    """
    sec_of_day = (acutime-1)*60*60*24
    year = datetime.datetime.now().year
    gyear = calendar.timegm(time.strptime(str(year), '%Y'))
    comptime = gyear+sec_of_day
    return comptime

def check_status_keys(acu, fallback_dataset='DataSets.StatusGeneral8100'):
    platform = acu._config.get('platform')
    if platform is None:
        print('Error: ACU configuration does not specify "platform"')
        print(f'Trying dataset="{fallback_dataset}"')
        dataset_opts = {}
        ds = [fallback_dataset]
    else:
        cfg = aculib.configs.get_datasets(platform)
        dataset_opts = {short: full_name for short, full_name in cfg['datasets']}
        ds = [cfg['default_dataset']]
        third_ds = acu._config['status'].get('3rdaxis_name')
        if third_ds is not None:
            ds.append(third_ds)

    status_keys_from_acu = []
    for n in ds:
        m = dataset_opts.get(n, n)
        try:
            bnow = time.time()
            t = acu.Values(m)
            time_diff = timecode(t['Time'])-bnow
        except aculib.http.HttpError as e:
            print('# error requesting dataset "%s"!' % m)
            continue
        print(f'# Using "{m}"')
        for k, v in t.items():
            if k not in status_keys_from_acu:
                # if block here because 3rd axis includes Time, Year
                status_keys_from_acu.append(k)
    status_keys_from_acu.sort()

    if platform is None:
        print('# Cannot compare keys to list because platform not declared.')
        statkey_check = False
        missing_keys, extra_keys = [], []
    else:
        key_list = status_keys.allkeys(platform)
        key_list.sort()
        missing_keys = []
        extra_keys = []
        if status_keys_from_acu == key_list:
            print('Status key lists match')
            statkey_check = True
        else:
            print('Mismatch of status keys. Please compare lists.')
            print()
            for key in key_list:
                if key not in status_keys_from_acu:
                    print('ACU does not have key "%s"' % key)
                    extra_keys.append(key)
            print()
            for acukey in status_keys_from_acu:
                if acukey not in key_list:
                    print('soaculib.status_keys does not have key "%s"' %acukey)
                    missing_keys.append(acukey)
            print()
            statkey_check = False

    print('ACU time - CPU time = %+.6f seconds' % time_diff)
    if abs(time_diff) > 0.1:
        print('Timing difference > 0.1 seconds!')
        timecheck = False
    else:
        print('Timing difference ok.')
        timecheck = True
    return statkey_check, timecheck, missing_keys, extra_keys

def az_stop_test(az, el):
    last_20_azpts = []
    moving = True
    acu.go_to(az, el)
    report_t = time.time()
    report_period = 20
    n_ok = 0
    min_query_period = 0.05
    query_t = 0
    while moving:
        now = time.time()
        if now > report_t + report_period:
            report_t = now
            n_ok = 0

        if now - query_t < min_query_period:
            yield dsleep(-(now - query_t-min_query_period))

        query_t = time.time()
        try:
            j = self.acu.http.Values(self.acu8100)
            n_ok += 1
            session.data = j
        except Exception as e:
            print(str(e))
            yield dsleep(1)
        while len(last_20_azpts) < 20:
            last_20_azpts.append(j['Azimuth current position'])
        print(last_20_azpts)


if __name__ == '__main__':
    import util
    acu = util.get_acu()

    status_key_check, timecheck, missing_keys, extra_keys = check_status_keys(acu)
    print('Status key check: ' + str(status_key_check))
    print('Status time difference check: ' + str(timecheck))

    result_file = open(str(time.time())+'_result.txt', 'w')
    result_file.write('Status key check result: ' + str(status_key_check) + '\r\n')
    if len(missing_keys):
        for key in missing_keys:
            result_file.write('Key missing from status_keys: ' + str(key) + '\r\n')
    else:
        result_file.write('No keys missing from status_keys\r\n')
    if len(extra_keys):
        for key in extra_keys:
            result_file.write('Key in status_keys but not ACU readout: ' + str(key) + '\r\n')
    else:
        result_file.write('No excess keys in status_keys\r\n')
    result_file.write('Status Time check result: ' + str(timecheck) + '\r\n')
    result_file.close()
