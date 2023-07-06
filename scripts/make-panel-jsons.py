"""
Print grafana panel JSON for ACU error bits.
"""

import json

false = False
true = True
null = None


class Renderer:
    def __init__(self, datasource_uid, measurement):
        self._datasource_uid = datasource_uid
        self._measurement = measurement
        self._index = None
        self._offset = None
        self._step = .02

    def one_field(self, alias, name, index=None, offset=None):
        if index is None:
            if self._index is None:
                self._index = 'A'
            else:
                self._index = chr(ord(self._index) + 1)
            index = self._index
        if offset is None:
            if self._offset is None:
                self._offset = 0.
            else:
                self._offset += self._step
            offset = self._offset

        return {
          "datasource": {
            "type": "influxdb",
            "uid": f"{self._datasource_uid}"
          },
          "alias": f"{alias}",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "previous"
              ],
              "type": "fill"
            }
          ],
          "measurement": f"{self._measurement}",
          "orderByTime": "ASC",
          "policy": "default",
          "refId": f"{index}",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                    f"{name}"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              },
              {
                "type": "math",
                "params": [
                   f"{offset:+.2f}"
                ]
              }
            ]
          ],
          "tags": [],
          "hide": false
        }

    def full_panel(self, title, fields):
        self._step = .6 / (len(fields) - 1)
        self._offset = -.3 - self._step
        TARGETS = [self.one_field(*f) for f in fields]
        return {
            "datasource": {
                "uid": f"{self._datasource_uid}",
                "type": "influxdb"
            },
            "fieldConfig": {
                "defaults": {
                    "custom": {
                        "drawStyle": "line",
                        "lineInterpolation": "linear",
                        "barAlignment": 0,
                        "lineWidth": 1,
                        "fillOpacity": 0,
                        "gradientMode": "none",
                        "spanNulls": false,
                        "showPoints": "auto",
                        "pointSize": 5,
                        "stacking": {
                            "mode": "none",
                            "group": "A"
                        },
                        "axisPlacement": "auto",
                        "axisLabel": "",
                        "axisColorMode": "text",
                        "scaleDistribution": {
                            "type": "linear"
                        },
                        "axisCenteredZero": false,
                        "hideFrom": {
                            "tooltip": false,
                            "viz": false,
                            "legend": false
                        },
                        "thresholdsStyle": {
                            "mode": "off"
                        }
                    },
                    "color": {
                        "mode": "palette-classic"
                    },
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {
                                "color": "green",
                                "value": null
                            },
                            {
                                "color": "red",
                                "value": 80
                            }
                        ]
                    }
                },
                "overrides": []
            },
            "gridPos": {
                "h": 8,
                "w": 12,
                "x": 0,
                "y": 0
            },
            "id": 10,
            "options": {
                "tooltip": {
                    "mode": "single",
                    "sort": "none"
                },
                "legend": {
                    "showLegend": true,
                    "displayMode": "list",
                    "placement": "bottom",
                    "calcs": []
                }
            },
            "targets": TARGETS,
            "title": f"{title}",
            "type": "timeseries"
        }


if 0:
    r = Renderer('e25f9c43-ed4d-4306-bdea-59d9a5197a0e',
                 'satp1.acu')

    data = r.full_panel('Azimuth Faults', [
        ('ccw2', 'AzCCW_HWlimit_emergency_influx'),
        ('ccw2', 'AzCCW_HWlimit_emergency_influx'),
    ])
    print(json.dumps(data))


import soaculib

import soaculib.status_keys as sf
data = sf.status_fields['satp']['status_fields']

def match_strip(panel, key):
    not_other = ['Azimuth_', 'Elevation_', 'Boresight_', 'Az', 'El', 'Bs']
    if panel == 'other':
        if any([key.startswith(k) for k in not_other]):
            return None
        return key
    if not (panel == 'bs' and key.lower().startswith('boresight')) and \
       not key.lower().startswith(panel):
        return None
    for no in not_other:
        if key.startswith(no):
            key = key[len(no):]
    return key

def get_panel_fields(verbose=False):
    def vprint(*args):
        if verbose:
            print(*args)
    fields = {}
    for panel in ['az', 'el', 'bs', 'other']:
        vprint(panel)
        for subset in ['limits', 'other']:
            if panel == 'other' and subset == 'limits':
                continue
            _fields = []
            fields[f'{panel}-{subset}'] = _fields
            if subset == 'limits':
                groups = ['axis_limits']
            else:
                groups = ['axis_faults_errors_overages', 'axis_warnings',
                      'axis_failures', 'axis_state', 'osc_alarms', 'ACU_failures_errors',
                      'platform_status', 'ACU_emergency']
            
            for group in groups:
                vprint('  ' + group)
                for k in data[group].values():
                    alias = match_strip(panel, k)
                    if alias is None:
                        continue
                    vprint('    ', k, alias)
                    _fields.append((alias, k + '_influx'))
    return fields


for k, fields in get_panel_fields().items():
    print(k, len(fields))
    for satp in [1,2,3]:
        r = Renderer('e25f9c43-ed4d-4306-bdea-59d9a5197a0e',
                     f'satp{satp}.acu')
        sys, grp = k.split('-')
        if sys == 'bs':
            sys = '3rd'
        if grp == 'limits':
            title = sys.capitalize() + ' Limits'
        elif sys == 'other':
            title = 'Global Faults'
        else:
            title = sys.capitalize() + ' Faults'

        data = r.full_panel(title, fields)
        text = json.dumps(data) + '\n'
        filename = f'panel-satp{satp}-{k}.json'
        print(f'Writing {filename} ("{title}")')
        open(filename, 'w').write(text)
