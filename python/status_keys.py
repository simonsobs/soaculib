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
                'Azimuth oscillation warning': 'Azimuth_oscillation_warning',
                'Elevation oscillation warning': 'Elevation_oscillation_warning',
                'Boresight oscillation warning': 'Boresight_oscillation_warning',
                },
            'axis_failures':    {
                'Azimuth servo failure': 'Azimuth_servo_failure',
                'Azimuth brake 1 failure': 'Azimuth_brake1_failure',
                'Azimuth brake 2 failure': 'Azimuth_brake2_failure',
                'Azimuth breaker failure': 'Azimuth_breaker_failure',
                'Azimuth amplifier power cylce interlock': 'Azimuth_power_cycle_interlock',
                'Azimuth amplifier 1 failure': 'Azimuth_amp1_failure',
                'Azimuth amplifier 2 failure': 'Azimuth_amp2_failure',
                'Azimuth CAN bus amplifier 1 communication failure': 'Az_CANbus_amp1_comms_failure',
                'Azimuth CAN bus amplifier 2 communication failure': 'Az_CANbus_amp2_comms_failure',
                'Azimuth encoder failure': 'Azimuth_encoder_failure',
                'Azimuth tacho failure': 'Azimuth_tacho_failure',
                'Elevation servo failure': 'Elevation_servo_failure',
                'Elevation brake 1 failure': 'Elevation_brake1_failure',
                'Elevation breaker failure': 'Elevation_breaker_failure',
                'Elevation amplifier power cylce interlock': 'Elevation_power_cycle_interlock',
                'Elevation amplifier 1 failure': 'Elevation_amp1_failure',
                'Elevation CAN bus amplifier 1 communication failure': 'El_CANbus_amp1_comms_failure',
                'Elevation encoder failure': 'Elevation_encoder_failure',
                'Boresight servo failure': 'Boresight_servo_failure',
                'Boresight brake 1 failure': 'Boresight_brake1_failure',
                'Boresight brake 2 failure': 'Boresight_brake2_failure',
                'Boresight breaker failure': 'Boresight_breaker_failure',
                'Boresight amplifier power cylce interlock': 'Boresight_power_cycle_interlock',
                'Boresight amplifier 1 failure': 'Boresight_amp1_failure',
                'Boresight amplifier 2 failure': 'Boresight_amp2_failure',
                'Boresight CAN bus amplifier 1 communication failure': 'Bs_CANbus_amp1_comms_failure',
                'Boresight CAN bus amplifier 2 communication failure': 'Bs_CANbus_amp2_comms_failure',
                'Boresight encoder failure': 'Boresight_encoder_failure',
                'Boresight tacho failure': 'Boresight_tacho_failure',
                },
            'axis_state':    {
                'Azimuth computer disabled': 'Azimuth_computer_disabled',
                'Azimuth axis disabled': 'Azimuth_disabled',
                'Azimuth axis in stop': 'Azimuth_axis_stop',
                'Azimuth brakes released': 'Azimuth_brakes_released',
                'Azimuth stop at LCP': 'Azimuth_stop_LCP',
                'Azimuth power on': 'Azimuth_power_on',
                'Azimuth AUX 1 mode selected': 'Azimuth_AUX1_mode_selected',
                'Azimuth AUX 2 mode selected': 'Azimuth_AUX2_mode_selected',
                'Azimuth immobile': 'Azimuth_immobile',
                'Elevation computer disabled': 'Elevation_computer_disabled',
                'Elevation axis disabled': 'Elevation_disabled',
                'Elevation axis in stop': 'Elevation_axis_stop',
                'Elevation brakes released': 'Elevation_brakes_released',
                'Elevation stop at LCP': 'Elevation_stop_LCP',
                'Elevation power on': 'Elevation_power_on',
                'Elevation immobile': 'Elevation_immobile',
                'Boresight computer disabled': 'Boresight_computer_disabled',
                'Boresight axis disabled': 'Boresight_disabled',
                'Boresight axis in stop': 'Boresight_axis_stop',
                'Boresight brakes released': 'Boresight_brakes_released',
                'Boresight stop at LCP': 'Boresight_stop_LCP',
                'Boresight power on': 'Boresight_power_on',
                'Boresight AUX 1 mode selected': 'Boresight_AUX1_mode_selected',
                'Boresight AUX 2 mode selected': 'Boresight_AUX2_mode_selected',
                'Boresight immobile': 'Boresight_immobile',
                },
            'osc_alarms':    {
                'Azimuth oscillation alarm': 'Azimuth_oscillation_alarm',
                'Elevation oscillation alarm': 'Elevation_oscillation_alarm',
                'Boresight oscillation alarm': 'Boresight_oscillation_alarm',
                },
            'commands':    {
                'Azimuth commanded position': 'Azimuth_commanded_position',
                'Elevation commanded position':  'Elevation_commanded_position',
                'Boresight commanded position': 'Boresight_commanded_position',
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
                'Program Track position failure': 'ProgramTrack_position_failure',
                'Start of Program Track too early': 'Track_start_too_early',
                'Turnaround acceleration too high': 'Turnaround_accel_too_high',
                'Turnaround time too short': 'Turnaround_time_too_short',
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
        },
    'ccat' : {
        'status_fields' : {
            'summary' : {
                'Time': 'Time',
                'Year': 'Year',
                'Azimuth mode': 'Azimuth_mode',
                'Azimuth current position': 'Azimuth_current_position',
                'Azimuth current velocity': 'Azimuth_current_velocity',
                'Elevation mode': 'Elevation_mode',
                'Elevation current position': 'Elevation_current_position',
                'Elevation current velocity': 'Elevation_current_velocity',
                'Qty of free program track stack positions': 'Free_upload_positions',
                },
            'position_errors' : {
                'Azimuth average position error': 'Azimuth_avg_position_error',
                'Azimuth peak position error': 'Azimuth_peak_position_error',
                'Elevation average position error': 'Elevation_avg_position_error',
                'Elevation peak position error': 'Elevation_peak_position_error',
                },
            'axis_limits' : {
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
                'Elevation Down limit: 2nd emergency': 'ElDown_HWlimit_2ndEmergency',
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
                'Elevation Up limit: 2nd emergency': 'ElUp_HWlimit_2ndEmergency',
                },
            'axis_faults_errors_overages' : {
                'Azimuth summary fault': 'Azimuth_summary_fault',
                'Azimuth motion error': 'Azimuth_motion_error',
                'Azimuth motor 1 overtemperature': 'Azimuth_motor1_overtemp',
                'Azimuth motor 2 overtemperature': 'Azimuth_motor2_overtemp',
                'Azimuth motor 3 overtemperature': 'Azimuth_motor3_overtemp',
                'Azimuth motor 4 overtemperature': 'Azimuth_motor4_overtemp',
                'Azimuth overspeed': 'Azimuth_overspeed',
                'Azimuth regeneration resistor 1 overtemperature': 'Azimuth_resistor1_overtemp',
                'Azimuth regeneration resistor 2 overtemperature': 'Azimuth_resistor2_overtemp',
                'Azimuth regeneration resistor 3 overtemperature': 'Azimuth_resistor3_overtemp',
                'Azimuth regeneration resistor 4 overtemperature': 'Azimuth_resistor4_overtemp',
                'Azimuth overcurrent motor 1': 'Azimuth_motor1_overcurrent',
                'Azimuth overcurrent motor 2': 'Azimuth_motor2_overcurrent',
                'Azimuth overcurrent motor 3': 'Azimuth_motor3_overcurrent',
                'Azimuth overcurrent motor 4': 'Azimuth_motor4_overcurrent',
                'Elevation summary fault': 'Elevation_summary_fault',
                'Elevation motion error': 'Elevation_motion_error',
                'Elevation motor 1 overtemperature': 'Elevation_motor1_overtemp',
                'Elevation motor 2 overtemperature': 'Elevation_motor2_overtemp',
                'Elevation overspeed': 'Elevation_overspeed',
                'Elevation regeneration resistor 1 overtemperature': 'Elevation_resistor1_overtemp',
                'Elevation regeneration resistor 2 overtemperature': 'Elevation_resistor2_overtemp',
                'Elevation overcurrent motor 1': 'Elevation_motor1_overcurrent',
                'Elevation overcurrent motor 2': 'Elevation_motor2_overcurrent',
                },
            'axis_warnings' : {
                'Azimuth gearbox 1 low oil level': 'Azimuth_gearbox1_low_oil',
                'Azimuth gearbox 2 low oil level': 'Azimuth_gearbox2_low_oil',
                'Azimuth gearbox 3 low oil level': 'Azimuth_gearbox3_low_oil',
                'Azimuth gearbox 4 low oil level': 'Azimuth_gearbox4_low_oil',
                'Azimuth oscillation warning': 'Azimuth_osc_warning',
                'Elevation gearbox 1 low oil level': 'Elevation_gearbox1_low_oil',
                'Elevation gearbox 2 low oil level': 'Elevation_gearbox2_low_oil',
                'Elevation oscillation warning': 'Elevation_osc_warning',
                },
            'axis_failures' : {
                'Azimuth servo failure': 'Azimuth_servo_failure',
                'Azimuth brake 1 failure': 'Azimuth_brake1_failure',
                'Azimuth brake 2 failure': 'Azimuth_brake2_failure',
                'Azimuth brake 3 failure': 'Azimuth_brake3_failure',
                'Azimuth brake 4 failure': 'Azimuth_brake4_failure',
                'Azimuth breaker failure': 'Azimuth_breaker_failure',
                'Azimuth amplifier 1 failure': 'Azimuth_amp1_failure',
                'Azimuth amplifier 2 failure': 'Azimuth_amp2_failure',
                'Azimuth amplifier 3 failure': 'Azimuth_amp3_failure',
                'Azimuth amplifier 4 failure': 'Azimuth_amp4_failure',
                'Azimuth Secondary Encoder Failure': 'Azimuth_secondary_encoder_failure',
                'Azimuth DC bus 1 failure': 'Az_DCbus1_failure',
                'Azimuth DC bus 2 failure': 'Az_DCbus2_failure',
                'Azimuth CAN bus amplifier 1 communication failure': 'Az_CANbus_amp1_comms_failure',
                'Azimuth CAN bus amplifier 2 communication failure': 'Az_CANbus_amp2_comms_failure',
                'Azimuth CAN bus amplifier 3 communication failure': 'Az_CANbus_amp3_comms_failure',
                'Azimuth CAN bus amplifier 4 communication failure': 'Az_CANbus_amp4_comms_failure',
                'Azimuth encoder failure': 'Azimuth_encoder_failure',
                'Azimuth tacho failure': 'Azimuth_tacho_failure',
                'Elevation servo failure': 'Elevation_servo_failure',
                'Elevation brake 1 failure': 'Elevation_brake1_failure',
                'Elevation brake 2 failure': 'Elevation_brake2_failure',
                'Elevation breaker failure': 'Elevation_breaker_failure',
                'Elevation amplifier 1 failure': 'Elevation_amp1_failure',
                'Elevation amplifier 2 failure': 'Elevation_amp2_failure',
                'Elevation Secondary Encoder Failure': 'Elevation_secondary_encoder_failure',
                'Elevation CAN bus amplifier 1 communication failure': 'El_CANbus_amp1_comms_failure',
                'Elevation CAN bus amplifier 2 communication failure': 'El_CANbus_amp2_comms_failure',
                'Elevation encoder failure': 'Elevation_encoder_failure',
                'Elevation tacho failure': 'Elevation_tacho_failure',
                },
            'axis_state' : {
                'Azimuth computer disabled': 'Azimuth_computer_disabled',
                'Azimuth axis disabled': 'Azimuth_disabled',
                'Azimuth axis in stop': 'Azimuth_axis_stop',
                'Azimuth brakes released': 'Azimuth_brakes_released',
                'Azimuth stop at LCP': 'Azimuth_stop_LCP',
                'Azimuth power on': 'Azimuth_power_on',
                'Azimuth AUX 1 mode selected': 'Azimuth_AUX1_mode_selected',
                'Azimuth AUX 2 mode selected': 'Azimuth_AUX2_mode_selected',
                'Azimuth amplifier power cycle interlock': 'Az_amp_power_cycle_interlock',
                'Azimuth immobile': 'Azimuth_immobile',
                'Elevation computer disabled': 'Elevation_computer_disabled',
                'Elevation axis disabled': 'Elevation_disabled',
                'Elevation axis in stop': 'Elevation_axis_stop',
                'Elevation brakes released': 'Elevation_brakes_released',
                'Elevation stop at LCP': 'Elevation_stop_LCP',
                'Elevation power on': 'Elevation_power_on',
                'Elevation AUX 1 mode selected': 'Elevation_AUX1_mode_selected',
                'Elevation AUX 2 mode selected': 'Elevation_AUX2_mode_selected',
                'Elevation amplifier power cycle interlock': 'El_amp_power_cycle_interlock',
                'Elevation immobile': 'Elevation_immobile',
                },
            'osc_alarms' : {
                'Azimuth oscillation alarm': 'Azimuth_osc_alarm',
                'Elevation oscillation alarm': 'Elevation_osc_alarm',
                },
            'commands' : {
                'Azimuth commanded position': 'Azimuth_commanded_position',
                'Elevation commanded position':  'Elevation_commanded_position',
                'Co-Rotator commanded position': 'Corotator_commanded_position',
                },
            'ACU_failures_errors' : {
                'General summary fault': 'General_summary_fault',
                'Power failure (latched)': 'Power_failure_latched',
                'Power failure (not latched)': 'Power_failure_not_latched',
                '24V power failure': 'Power_failure_24V',
                'General Breaker failure': 'General_breaker_failure',
                'Cabinet Overtemperature': 'Cabinet_overtemp',
                'Cabinet undertemperature': 'Cabinet_undertemp',
                'Profinet Error': 'Profinet_error',
                'Ambient temperature low (operation inhibited)': 'Ambient_low_temp',
                'PLC-ACU interface error': 'PLC_ACU_interface_error',
                'ACU fan failure': 'ACU_fan_failure',
                'Time synchronisation error': 'Time_sync_error',
                'ACU-PLC communication error': 'ACU_PLC_comms_error',
                'Program Track position failure': 'ProgramTrack_position_failure',
                'Start of Program Track too early': 'Track_start_too_early',
                'Turnaround acceleration too high': 'Turnaround_accel_too_high',
                'Turnaround time too short': 'Turnaround_time_too_short',
                },
            'platform_status' : {
                'Access Hatch Interlock - Support Cone': 'Interlock_AccessHatch_SupportCone',
                'Yoke A Door Warning - Outside to Stairway': 'Warn_YokeADoor_OutsideStairway',
                'Stairway Door Warning - Yoke Traverse': 'Warn_StairwayDoor_YokeTraverse',
                'Ladder Interlock - Yoke Traverse': 'Interlock_Ladder_YokeTraverse',
                'Yoke A Door Interlock - 3rd Floor': 'Interlock_YokeADoor_3rdFloor',
                'Floor Hatch Interlock - Instrument Space 1': 'Interlock_FloorHatch_Instrument1',
                'Material Door Warning - Instrument Space': 'Warn_MaterialDoor_Instrument',
                'Yoke A Door Interlock - 2nd Floor': 'Interlock_YokeADoor_2ndFloor',
                'Yoke B Door Warning - Traverse to 1st Floor': 'Warn_YokeBDoor_Traverse1stFloor',
                'Access Hatch Interlock - Roof Yoke B': 'Interlock_AccessHatch_RoofYokeB',
                'Yoke Traverse: Electronics space hoist position': 'Warn_ElecSpace_HoistPos_YokeTraverse',
                'Drive cabinet door': 'Warn_DriveCabinetDoor',
                'Hoist storage container': 'Warn_Hoist_StorageContainer',
                'Elevation Stowpin Failure': 'El_Stowpin_Failure',
                'Elevation Stowpin Status': 'El_Stowpin_Status',
                'Elevation Stowpin Timeout': 'El_Stowpin_Timeout',
                'Key Switch Safe Override': 'Key_Switch_Safe_Override',
                'Key Switch Bypass Emergency Limit': 'Key_Switch_Bypass_Emergency_Limit',
                'PCU operation': 'PCU_operation',
                'Safe': 'Safe_mode',
                'Lightning protection surge arresters': 'Lightning_protection_surge_arresters',
                'Crane on': 'Crane_on',
                'ACU in remote mode': 'Remote_mode',
                },
            'ACU_emergency' : {
                'E-Stop Device': 'EStop_device',
                'E-Stop Servo Drive Cabinet': 'EStop_servo_drive_cabinet',
                'E-Stop Az Drives 1+2': 'EStop_AzDrives_12',
                'E-Stop Az Drives 3+4': 'EStop_AzDrives_34',
                'E-Stop El Drives': 'EStop_ElDrives',
                'E-Stop Staircase Lower End': 'EStop_staircase_lower',
                'E-Stop Elevator Access': 'EStop_Elevator_access',
                'E-Stop Instrument Space 1, Co-Rotator': 'EStop_Instrument_Space1_CoRotator',
                'E-Stop El Housing, Mirror Area': 'EStop_ElHousing_Mirror',
                'E-Stop MPD': 'EStop_MPD',
                'E-Stop OCS': 'EStop_OCS',
                'E-Stop PCU': 'EStop_PCU',
                },
            'corotator': {
                'Co-Rotator mode': 'Corotator_mode',
                'Co-Rotator current position': 'Corotator_current_position',
                'Co-Rotator computer disabled': 'Corotator_computer_disabled',
                'Co-Rotator axis in stop': 'Corotator_axis_stop',
                'Co-Rotator axis disabled': 'Corotator_disabled',
                'Co-Rotator brakes released': 'Corotator_brakes_released',
                'Co-Rotator stop at LCP': 'Corotator_stop_LCP',
                'Co-Rotator power on': 'Corotator_power_on',
                'Co-Rotator CCW limit: 2nd emergency' : 'CorotCCW_HWlimit_2ndEmergency',
                'Co-Rotator CCW limit: emergency' : 'CorotCCW_HWlimit_emergency',
                'Co-Rotator CCW limit: operating' : 'CorotCCW_HWlimit_operating',
                'Co-Rotator CCW limit: pre-limit' : 'CorotCCW_HWprelimit',
                'Co-Rotator CCW limit: operating (ACU software limit)' : 'CorotCCW_SWlimit_operating',
                'Co-Rotator CCW limit: pre-limit (ACU software limit)' : 'CorotCCW_SWprelim',
                'Co-Rotator CW limit: pre-limit (ACU software limit)' : 'CorotCW_SWprelim',
                'Co-Rotator CW limit: operating (ACU software limit)' : 'CorotCW_SWlimit_operating',
                'Co-Rotator CW limit: pre-limit' : 'CorotCW_HWprelimit',
                'Co-Rotator CW limit: operating' : 'CorotCW_HWlimit_operating_',
                'Co-Rotator CW limit: emergency' : 'CorotCW_HWlimit_emergency',
                'Co-Rotator CW limit: 2nd emergency' : 'CorotCW_HWlimit_2ndEmergency',
                'Co-Rotator summary fault' : 'Corotator_summary_fault',
                'Co-Rotator servo failure' : 'Corotator_servo_failure',
                'Co-Rotator brake 1 failure' : 'Corotator_brake1_failure',
                'Co-Rotator breaker failure' : 'Corotator_breaker_failure',
                'Co-Rotator amplifier 1 failure' : 'Corotator_amp1_failure',
                'Co-Rotator motor 1 overtemperature' : 'Corotator_motor1_overtemp',
                'Co-Rotator overspeed' : 'Corotator_overspeed',
                'Co-Rotator amplifier power cycle interlock': 'Corotator_amp_power_cycle_interlock',
                'Co-Rotator regeneration resistor 1 overtemperature' : 'Corotator_resistor1_overtemp',
                'Co-Rotator CAN bus amplifier 1 communication failure' : 'Corotator_CANbus_amp1_comms_failure',
                'Co-Rotator encoder failure' : 'Corotator_encoder_failure',
                'Co-Rotator oscillation warning' : 'Corotator_oscillation_warning',
                'Co-Rotator oscillation alarm' : 'Corotator_oscillation_alarm',
                'Co-Rotator immobile' : 'Corotator_immobile',
                'Co-Rotator overcurrent motor 1' : 'Corotator_motor1_overcurrent',
                },
            },
        },
    }

def allkeys(platform_type):
    all_keys = []
    pfd = status_fields[platform_type]['status_fields']
    for category in pfd.keys():
        for key in pfd[category].keys():
            all_keys.append(key)
    return all_keys
