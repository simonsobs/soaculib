status_fields = {
    'satp' : {
        'status_fields':   {
            'summary':    {
                'Time': 'Time',
                'Year': 'Year',
                'Azimuth mode': 'Azimuth_mode',
                'Azimuth current position': 'Azimuth_current_position',
                'Azimuth current velocity': 'Azimuth_current_velocity',
                'Elevation mode': 'Elevation_mode',
                'Elevation current position': 'Elevation_current_position',
                'Elevation current velocity': 'Elevation_current_velocity',
                'Boresight mode': 'Boresight_mode',
                'Boresight current position': 'Boresight_current_position',
                'Qty of free program track stack positions': 'Free_upload_positions',
                },
            'position_errors':    {
                'Azimuth average position error': 'Azimuth_avg_position_error',
                'Azimuth peak position error': 'Azimuth_peak_position_error',
                'Elevation average position error': 'Elevation_avg_position_error',
                'Elevation peak position error': 'Elevation_peak_position_error',
                },
            'axis_limits':    {
                'Azimuth CCW limit: 2nd emergency': 'AzCCW_HWlimit_2ndEmergency',
                'Azimuth CCW limit: emergency': 'AzCCW_HWlimit_emergency',
                'Azimuth CCW limit: operating': 'AzCCW_HWlimit_operating',
                'Azimuth CCW limit: pre-limit': 'AzCCW_HWprelimit',
                'Azimuth CCW limit: operating (ACU software limit)': 'AzCCW_SWlimit_operating',
                'Azimuth CCW limit: pre-limit (ACU software limit)': 'AzCCW_SWprelimit',
                'Azimuth CW limit: pre-limit (ACU software limit)': 'AzCW_SWprelimit',
                'Azimuth CW limit: operating (ACU software limit)': 'AzCW_SWlimit_operating',
                'Azimuth CW limit: pre-limit': 'AzCW_HWprelimit',
                'Azimuth CW limit: operating': 'AzCW_HWlimit_operating',
                'Azimuth CW limit: emergency': 'AzCW_HWlimit_emergency',
                'Azimuth CW limit: 2nd emergency': 'AzCW_HWlimit_2ndEmergency',
                'Elevation Down limit: extended emergency (co-moving shield off)': 'ElDown_HWlimit_shieldOFF_emergency',
                'Elevation Down limit: extended operating (co-moving shield off)': 'ElDown_HWlimit_shieldOFF_operating',
                'Elevation Down limit: emergency': 'ElDown_HWlimit_emergency',
                'Elevation Down limit: operating': 'ElDown_HWlimit_operating',
                'Elevation Down limit: pre-limit': 'ElDown_HWprelimit',
                'Elevation Down limit: operating (ACU software limit)': 'ElDown_SWlimit_operating',
                'Elevation Down limit: pre-limit (ACU software limit)': 'ElDown_SWprelimit',
                'Elevation Up limit: pre-limit (ACU software limit)': 'ElUp_SWprelimit',
                'Elevation Up limit: operating (ACU software limit)': 'ElUp_SWlimit_operating',
                'Elevation Up limit: pre-limit': 'ElUp_HWprelimit',
                'Elevation Up limit: operating': 'ElUp_HWlimit_operating',
                'Elevation Up limit: emergency': 'ElUp_HWlimit_emergency',
                'Boresight CCW limit: emergency': 'BsCCW_HWlimit_emergency',
                'Boresight CCW limit: operating': 'BsCCW_HWlimit_operating',
                'Boresight CCW limit: pre-limit': 'BsCCW_HWprelimit',
                'Boresight CCW limit: operating (ACU software limit)': 'BsCCW_SWlimit_operating',
                'Boresight CCW limit: pre-limit (ACU software limit)': 'BsCCW_SWprelimit',
                'Boresight CW limit: pre-limit (ACU software limit)': 'BsCW_SWprelimit',
                'Boresight CW limit: operating (ACU software limit)': 'BsCW_SWlimit_operating',
                'Boresight CW limit: pre-limit': 'BsCW_HWprelimit',
                'Boresight CW limit: operating': 'BsCW_HWlimit_operating',
                'Boresight CW limit: emergency': 'BsCW_HWlimit_emergency',
                },
            'axis_faults_errors_overages':    {
                'Azimuth summary fault': 'Azimuth_summary_fault',
                'Azimuth motion error': 'Azimuth_motion_error',
                'Azimuth motor 1 overtemperature': 'Azimuth_motor1_overtemp',
                'Azimuth motor 2 overtemperature': 'Azimuth_motor2_overtemp',
                'Azimuth overspeed': 'Azimuth_overspeed',
                'Azimuth regeneration resistor 1 overtemperature': 'Azimuth_resistor1_overtemp',
                'Azimuth regeneration resistor 2 overtemperature': 'Azimuth_resistor2_overtemp',
                'Azimuth overcurrent motor 1': 'Azimuth_motor1_overcurrent',
                'Azimuth overcurrent motor 2': 'Azimuth_motor2_overcurrent',
                'Elevation summary fault': 'Elevation_summary_fault',
                'Elevation motion error': 'Elevation_motion_error',
                'Elevation motor 1 overtemp': 'Elevation_motor1_overtemp',
                'Elevation overspeed': 'Elevation_overspeed',
                'Elevation regeneration resistor 1 overtemperature': 'Elevation_resistor1_overtemp',
                'Elevation overcurrent motor 1': 'Elevation_motor1_overcurrent',
                'Boresight summary fault': 'Boresight_summary_fault',
                'Boresight motion error': 'Boresight_motion_error',
                'Boresight motor 1 overtemperature': 'Boresight_motor1_overtemp',
                'Boresight motor 2 overtemperature': 'Boresight_motor2_overtemp',
                'Boresight overspeed': 'Boresight_overspeed',
                'Boresight regeneration resistor 1 overtemperature': 'Boresight_resistor1_overtemp',
                'Boresight regeneration resistor 2 overtemperature': 'Boresight_resistor1_overtemp',
                'Boresight overcurrent motor 1': 'Boresight_motor1_overcurrent',
                'Boresight overcurrent motor 2': 'Boresight_motor2_overcurrent',
                },
            'axis_warnings':    {
#                'Azimuth brake warning': 'Azimuth_brake_warning',
                'Azimuth oscillation warning': 'Azimuth_oscillation_warning',
#                'Elevation brake warning': 'Elevation_brake_warning',
                'Elevation oscillation warning': 'Elevation_oscillation_warning',
#                'Boresight brake warning': 'Boresight_brake_warning',
                'Boresight oscillation warning': 'Boresight_oscillation_warning',
                },
            'axis_failures':    {
                'Azimuth servo failure': 'Azimuth_servo_failure',
                'Azimuth brake 1 failure': 'Azimuth_brake1_failure',
                'Azimuth brake 2 failure': 'Azimuth_brake2_failure',
                'Azimuth breaker failure': 'Azimuth_breaker_failure',
                'Azimuth amplifier 1 failure': 'Azimuth_amplifier1_failure',
                'Azimuth amplifier 2 failure': 'Azimuth_amplifier2_failure',
                'Azimuth CAN bus amplifier 1 communication failure': 'Az_CANbus_amp1_comms_failure',
                'Azimuth CAN bus amplifier 2 communication failure': 'Az_CANbus_amp2_comms_failure',
                'Azimuth encoder failure': 'Azimuth_encoder_failure',
                'Azimuth tacho failure': 'Azimuth_tacho_failure',
                'Elevation servo failure': 'Elevation_servo_failure',
                'Elevation brake 1 failure': 'Elevation_brake1_failure',
                'Elevation breaker failure': 'Elevation_breaker_failure',
                'Elevation amplifier 1 failure': 'Elevation_amplifier1_failure',
                'Elevation CAN bus amplifier 1 communication failure': 'El_CANbus_amp1_comms_failure',
                'Elevation encoder failure': 'Elevation_encoder_failure',
                'Boresight servo failure': 'Boresight_servo_failure',
                'Boresight brake 1 failure': 'Boresight_brake1_failure',
                'Boresight brake 2 failure': 'Boresight_brake2_failure',
                'Boresight breaker failure': 'Boresight_breaker_failure',
                'Boresight amplifier 1 failure': 'Boresight_amplifier1_failure',
                'Boresight amplifier 2 failure': 'Boresight_amplifier2_failure',
                'Boresight CAN bus amplifier 1 communication failure': 'Bs_CANbus_amp1_comms_failure',
                'Boresight CAN bus amplifier 2 communication failure': 'Bs_CANbus_amp2_comms_failure',
                'Boresight encoder failure': 'Boresight_encoder_failure',
                'Boresight tacho failure': 'Boresight_tacho_failure',
                },
            'axis_state':    {
                'Azimuth computer disabled': 'Azimuth_computer_disabled',
                'Azimuth axis disabled': 'Azimuth_axis_disabled',
                'Azimuth axis in stop': 'Azimuth_axis_stop',
                'Azimuth brakes released': 'Azimuth_brakes_released',
                'Azimuth stop at LCP': 'Azimuth_stop_LCP',
                'Azimuth power on': 'Azimuth_power_on',
                'Azimuth AUX 1 mode selected': 'Azimuth_AUX1_mode_selected',
                'Azimuth AUX 2 mode selected': 'Azimuth_AUX2_mode_selected',
                'Azimuth amplifier power cylce interlock': 'Azimuth_amp_power_cycle_interlock',
                'Azimuth immobile': 'Azimuth_immobile',
                'Elevation computer disabled': 'Elevation_computer_disabled',
                'Elevation axis disabled': 'Elevation_axis_disabled',
                'Elevation axis in stop': 'Elevation_axis_stop',
                'Elevation brakes released': 'Elevation_brakes_released',
                'Elevation stop at LCP': 'Elevation_stop_LCP',
                'Elevation power on': 'Elevation_power_on',
                'Elevation amplifier power cylce interlock': 'Elevation_amp_power_cycle_interlock',
                'Elevation immobile': 'Elevation_immobile',
                'Boresight computer disabled': 'Boresight_computer_disabled',
                'Boresight axis disabled': 'Boresight_axis_disabled',
                'Boresight axis in stop': 'Boresight_axis_stop',
                'Boresight brakes released': 'Boresight_brakes_released',
                'Boresight stop at LCP': 'Boresight_stop_LCP',
                'Boresight power on': 'Boresight_power_on',
                'Boresight AUX 1 mode selected': 'Boresight_AUX1_mode_selected',
                'Boresight AUX 2 mode selected': 'Boresight_AUX2_mode_selected',
                'Boresight amplifier power cylce interlock': 'Boreight_amp_power_cycle_interlock',
                'Boresight immobile': 'Boresight_immobile',
                },
            'osc_alarms':    {
                'Azimuth oscillation alarm': 'Azimuth_oscillation_alarm',
                'Elevation oscillation alarm': 'Elevation_oscillation_alarm',
                'Boresight oscillation alarm': 'Boresight_oscillation_alarm',
                },
            'commands':    {
                'Azimuth commanded position': 'Azimuth_Preset_position',
                'Elevation commanded position':  'Elevation_Preset_position',
                'Boresight commanded position': 'Boresight_Preset_position',
                },
            'ACU_failures_errors':    {
                'General summary fault': 'General_summary_fault',
                'Power failure (latched)': 'Power_failure_Latched',
                '24V power failure': 'Power_failure_24V',
                'General Breaker failure': 'General_breaker_failure',
                'Power failure (not latched)': 'Power_failure_NotLatched',
                'Cabinet Overtemperature': 'Cabinet_overtemp',
                'Ambient temperature low (operation inhibited)': 'Ambient_temp_TooLow',
                'PLC-ACU interface error': 'PLC_interface_error',
                'ACU fan failure': 'ACU_fan_failure',
                'Cabinet undertemperature': 'Cabinet_undertemp',
                'Time synchronisation error': 'Time_sync_error',
                'ACU-PLC communication error': 'PLC_comms_error',
                },
            'platform_status':    {
                'PCU operation': 'PCU_operation',
                'Safe': 'Safe_mode',
                'Lightning protection surge arresters': 'Lightning_protection_surge_arresters',
                'Co-Moving Shield off': 'CoMoving_shield_off',
                'ACU in remote mode': 'Remote_mode',
                },
            'ACU_emergency':    {
                'E-Stop servo drive cabinet': 'EStop_servo_drive_cabinet',
                'E-Stop service pole': 'EStop_service_pole',
                'E-Stop Az movable': 'EStop_Az_movable',
                'Key Switch Bypass Emergency Limit': 'Key_switch_bypass_emergency_limit',
                }
            }
        }
    }

def allkeys(platform_type):
    all_keys = []
    pfd = status_fields[platform_type]['status_fields']
    for category in pfd.keys():
        for key in pfd[category].keys():
            all_keys.append(key)
    return all_keys
