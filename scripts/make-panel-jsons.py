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
                "none"
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

    def full_panel(self, title, fields, pos=None, _id=None):
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
                        "showPoints": "always",
                        "pointSize": 2,
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
            "gridPos": pos,
            "id": _id,
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
    def full_dashboard(self, panels):
        panel_data = []
        for i, (t, f, (row, col)) in enumerate(panels):
            pos = {'h': 8, 'w': 12,
                   'x': 8 * col, 'y': 12 * row}
            panel_data.append(self.full_panel(t, f, pos=pos, _id=i))

        return {
            "annotations": {
                "list": [
                    {
                        "builtIn": 1,
                        "datasource": {
                            "type": "grafana",
                            "uid": "-- Grafana --"
                        },
                        "enable": true,
                        "hide": true,
                        "iconColor": "rgba(0, 211, 255, 1)",
                        "name": "Annotations & Alerts",
                        "target": {
                            "limit": 100,
                            "matchAny": false,
                            "tags": [],
                            "type": "dashboard"
                        },
                        "type": "dashboard"
                    }
                ]
            },
            "editable": true,
            "fiscalYearStartMonth": 0,
            "graphTooltip": 0,
            "id": 1,
            "links": [],
            "liveNow": false,
            "panels": panel_data,
            "refresh": "5s",
            "schemaVersion": 38,
            "style": "dark",
            "tags": [],
            "templating": {
                "list": []
            },
            "time": {
                "from": "now-5m",
                "to": "now"
            },
            "timepicker": {},
            "timezone": "",
            "title": "ACU Faults (SATP1)",
            #"uid": "MiMrVfF4k",
            #"version": 23,
            "weekStart": ""
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
    fields['other-limits'] = [
        ('az', 'Azimuth_current_position_influx'),
        ('el', 'Elevation_current_position_influx'),
        ('boresight', 'Boresight_current_position_influx')
    ]
        
    return fields


use_plat_var = True
if use_plat_var:
    platfmt = "/^$platform$/"
    satps = ['var']
else:
    platfmt = 'satp{satp}.acu'
    satps = [1, 2, 3]

for satp in satps:
    r = Renderer('e25f9c43-ed4d-4306-bdea-59d9a5197a0e',
                 platfmt.format(satp=satp))
    panels = {}
    for k, fields in get_panel_fields().items():
        print(k, len(fields))
        sys, grp = k.split('-')
        if sys == 'bs':
            sys = '3rd'
        if k == 'other-limits':
            title = 'Positions'
        elif grp == 'limits':
            title = sys.capitalize() + ' Limits'
        elif sys == 'other':
            title = 'Global Faults'
        else:
            title = sys.capitalize() + ' Faults'
        panels[k] = (title, fields)

    org = [
        ('other-other', 0, 0),
        ('az-other', 1, 0),
        ('el-other', 2, 0),
        ('bs-other', 3, 0),
        ('other-limits', 0, 1),
        ('az-limits', 1, 1),
        ('el-limits', 2, 1),
        ('bs-limits', 3, 1),
    ]

    for _id, (k, row, col) in enumerate(org):
        pos = {'h': 8, 'w': 12,
               'x': 12 * col, 'y': 8 * row}
        data = r.full_panel(panels[k][0], panels[k][1], pos=pos, _id=_id)
        text = json.dumps(data) + '\n'
        filename = f'panel-satp{satp}-{k}.json'
        print(f'Writing {filename}')
        open(filename, 'w').write(text)

    
        
