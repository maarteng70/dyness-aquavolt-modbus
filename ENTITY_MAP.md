# Dyness Aquavolt — entity map

Generated from `custom_components/dyness_modbus/registers/dyness.yaml` and
`translations/en.json` by `tools/gen_entities_md.py`. Do not edit by hand.

`<prefix>` is the device name slug chosen at setup (e.g. `M1`).

### sensor — polled from Modbus

| Entity | Register | Type | Unit | Enabled | Description |
|---|---|---|---|---|---|
| `sensor.<prefix>_modbus_protocol_version` | 0 | uint16 |  | no | Modbus Protocol Version — Modbus protocol version |
| `sensor.<prefix>_rated_power` | 1 | uint16 | W | yes | Rated Power — Rated power of the battery |
| `sensor.<prefix>_ac_output_type` | 2 | uint16 |  | no | AC Output Type — AC output type |
| `sensor.<prefix>_serial_number` | 3 | char x11 |  | yes | Serial Number — Serial number of the device |
| `sensor.<prefix>_dsp1_software_version` | 16 | uint16 |  | no | DSP1 Software Version — DSP1 software version |
| `sensor.<prefix>_dsp2_software_version` | 17 | uint16 |  | no | DSP2 Software Version — DSP2 software version |
| `sensor.<prefix>_dsp_svn_version` | 18 | uint16 |  | no | DSP SVN Version — DSP SVN version |
| `sensor.<prefix>_arm_software_version` | 19 | uint16 |  | no | ARM Software Version — ARM software version |
| `sensor.<prefix>_arm_svn_version` | 20 | uint16 |  | no | ARM SVN Version — ARM SVN version |
| `sensor.<prefix>_dsp_internal_firmware` | 21 | char x6 |  | no | DSP Internal Firmware — DSP internal firmware version |
| `sensor.<prefix>_arm_internal_firmware` | 27 | char x6 |  | no | ARM Internal Firmware — ARM internal firmware version |
| `sensor.<prefix>_device_hardware_version` | 33 | uint16 |  | no | Device Hardware Version — Device hardware version |
| `sensor.<prefix>_manufacture` | 35 | char x8 |  | yes | Manufacturer — Manufacturer name |
| `sensor.<prefix>_power_ratio` | 43 | uint16 |  | no | Power Ratio — Power ratio |
| `sensor.<prefix>_bms_version` | 51 | uint16 |  | no | BMS Version — BMS version |
| `sensor.<prefix>_ac_port_voltage_phase1` | 117 | uint16 | V | yes | AC Port Voltage (Phase 1) — AC Port Voltage (Phase 1) |
| `sensor.<prefix>_ac_port_current_phase1` | 118 | uint16 | A | yes | AC Port Current (Phase 1) — AC Port Current (Phase 1) |
| `sensor.<prefix>_ac_port_frequency_phase1` | 119 | uint16 | Hz | yes | AC Port Frequency (Phase 1) — AC Port Frequency (Phase 1) |
| `sensor.<prefix>_ac_port_power_phase1` | 120 | int16 | W | yes | AC Port Power (Phase 1) — AC Port Power (Phase 1) |
| `sensor.<prefix>_ac_port_voltage_phase2` | 122 | uint16 | V | no | AC Port Voltage (Phase 2) — AC Port Voltage (Phase 2) |
| `sensor.<prefix>_ac_port_current_phase2` | 123 | uint16 | A | no | AC Port Current (Phase 2) — AC Port Current (Phase 2) |
| `sensor.<prefix>_ac_port_frequency_phase2` | 124 | uint16 | Hz | no | AC Port Frequency (Phase 2) — AC Port Frequency (Phase 2) |
| `sensor.<prefix>_ac_port_power_phase2` | 125 | int16 | W | no | AC Port Power (Phase 2) — AC Port Power (Phase 2) |
| `sensor.<prefix>_ac_port_voltage_phase3` | 127 | uint16 | V | no | AC Port Voltage (Phase 3) — AC Port Voltage (Phase 3) |
| `sensor.<prefix>_ac_port_current_phase3` | 128 | uint16 | A | no | AC Port Current (Phase 3) — AC Port Current (Phase 3) |
| `sensor.<prefix>_ac_port_frequency_phase3` | 129 | uint16 | Hz | no | AC Port Frequency (Phase 3) — AC Port Frequency (Phase 3) |
| `sensor.<prefix>_ac_port_power_phase3` | 130 | int16 | W | no | AC Port Power (Phase 3) — AC Port Power (Phase 3) |
| `sensor.<prefix>_ac_port_mode` | 132 | uint16 |  | no | AC Port Mode — AC Port Mode (2 state labels) |
| `sensor.<prefix>_ac_port_power_total` | 133 | int16 | W | yes | AC Active Power — AC Active Power |
| `sensor.<prefix>_ac_port_reactive_power` | 135 | int16 | var | no | AC Reactive Power — AC Reactive Power |
| `sensor.<prefix>_ac_port_apparent_power` | 137 | int16 | VA | no | AC Apparent Power — AC Apparent Power |
| `sensor.<prefix>_ac_port_backup_power` | 143 | int16 | W | yes | AC Port Backup Power — AC Port Backup Power |
| `sensor.<prefix>_internal_temperature` | 164 | int16 | °C | yes | Internal Temperature — Internal temperature |
| `sensor.<prefix>_radiator_temperature` | 165 | int16 | °C | no | Radiator Temperature — Radiator temperature |
| `sensor.<prefix>_module_temperature` | 166 | int16 | °C | no | Module Temperature — Module temperature |
| `sensor.<prefix>_function_bit_value` | 167 | uint16 |  | no | Function Bit Value — Function bit value |
| `sensor.<prefix>_bus_voltage` | 168 | uint16 | V | no | Bus Voltage — Bus voltage |
| `sensor.<prefix>_nbus_voltage` | 169 | uint16 | V | no | NBus Voltage — NBus voltage |
| `sensor.<prefix>_battery_voltage` | 170 | uint16 | V | yes | Battery Voltage — Battery voltage |
| `sensor.<prefix>_battery_current` | 171 | int16 | A | yes | Battery Current — Battery current |
| `sensor.<prefix>_battery_power` | 172 | int16 | W | yes | Battery Power — Battery power |
| `sensor.<prefix>_battery_mode` | 173 | uint16 |  | yes | Battery Mode — Battery mode (6 state labels) |
| `sensor.<prefix>_warning_code` | 174 | uint16 |  | no | Warning Code — Warning code |
| `sensor.<prefix>_safety_country` | 175 | uint16 |  | no | Safety Country — Safety country (104 state labels) |
| `sensor.<prefix>_inverter_state` | 176 | uint16 |  | yes | Inverter State — Inverter state (6 state labels) |
| `sensor.<prefix>_pv_energy_total` | 181 | uint32 x2 | kWh | yes | PV Energy Total — PV Energy Total |
| `sensor.<prefix>_pv_energy_day` | 183 | uint16 | kWh | yes | PV Energy Today — PV Energy Today |
| `sensor.<prefix>_utility_to_grid_total` | 184 | uint32 x2 | kWh | yes | Utility to Grid Total — Utility to Grid Total |
| `sensor.<prefix>_utility_to_grid_day` | 188 | uint16 | kWh | yes | Utility to Grid Today — Utility to Grid Today |
| `sensor.<prefix>_utility_from_grid_total` | 189 | uint32 x2 | kWh | yes | Utility from Grid Total — Utility from Grid Total |
| `sensor.<prefix>_utility_from_grid_day` | 191 | uint16 | kWh | yes | Utility from Grid Today — Utility from Grid Today |
| `sensor.<prefix>_load_energy_total` | 192 | uint32 x2 | kWh | no | Load Energy Total — Load Energy Total |
| `sensor.<prefix>_load_energy_day` | 194 | uint16 | kWh | no | Load Energy Today — Load Energy Today |
| `sensor.<prefix>_battery_charge_energy_total` | 195 | uint32 x2 | kWh | yes | Battery Charge Energy Total — Battery Charge Energy Total |
| `sensor.<prefix>_battery_charge_energy_day` | 197 | uint16 | kWh | yes | Battery Charge Energy Today — Battery Charge Energy Today |
| `sensor.<prefix>_battery_discharge_energy_total` | 198 | uint32 x2 | kWh | yes | Battery Discharge Energy Total — Battery Discharge Energy Total |
| `sensor.<prefix>_battery_discharge_energy_day` | 200 | uint16 | kWh | yes | Battery Discharge Energy Today — Battery Discharge Energy Today |
| `sensor.<prefix>_cpld_code` | 201 | uint16 |  | no | CPLD Code — CPLD code |
| `sensor.<prefix>_battery_voltage_2` | 262 | uint16 | V | no | Battery 2 Voltage — Battery 2 Voltage |
| `sensor.<prefix>_battery_current_2` | 263 | int16 | A | no | Battery 2 Current — Battery 2 Current |
| `sensor.<prefix>_battery_power_2` | 264 | int16 | W | no | Battery 2 Power — Battery 2 Power |
| `sensor.<prefix>_battery_mode_2` | 265 | uint16 |  | no | Battery 2 Mode — Battery 2 Mode (6 state labels) |
| `sensor.<prefix>_utility_voltage_phase1` | 266 | uint16 | V | yes | Utility Voltage (Phase 1) — Utility Voltage (Phase 1) |
| `sensor.<prefix>_utility_current_phase1` | 267 | uint16 | A | yes | Utility Current (Phase 1) — Utility Current (Phase 1) |
| `sensor.<prefix>_utility_power_phase1` | 268 | int16 | W | yes | Utility Power (Phase 1) — Utility Power (Phase 1) |
| `sensor.<prefix>_utility_voltage_phase2` | 270 | uint16 | V | no | Utility Voltage (Phase 2) — Utility Voltage (Phase 2) |
| `sensor.<prefix>_utility_current_phase2` | 271 | uint16 | A | no | Utility Current (Phase 2) — Utility Current (Phase 2) |
| `sensor.<prefix>_utility_power_phase2` | 272 | int16 | W | no | Utility Power (Phase 2) — Utility Power (Phase 2) |
| `sensor.<prefix>_utility_voltage_phase3` | 274 | uint16 | V | no | Utility Voltage (Phase 3) — Utility Voltage (Phase 3) |
| `sensor.<prefix>_utility_current_phase3` | 275 | uint16 | A | no | Utility Current (Phase 3) — Utility Current (Phase 3) |
| `sensor.<prefix>_utility_power_phase3` | 276 | int16 | W | no | Utility Power (Phase 3) — Utility Power (Phase 3) |
| `sensor.<prefix>_utility_frequency` | 278 | uint16 | Hz | yes | Utility Frequency — Utility Frequency |
| `sensor.<prefix>_total_utility_power` | 385 | int16 | W | no | Total Utility Power — Total Utility Power |
| `sensor.<prefix>_bms_comm_status` | 2002 | uint16 |  | no | BMS Communication Status — BMS Communication Status (2 state labels) |
| `sensor.<prefix>_bms_soc` | 2010 | uint16 | % | yes | BMS SoC — BMS SoC |
| `sensor.<prefix>_bms_soh` | 2011 | uint16 | % | no | BMS SoH — BMS SoH |
| `sensor.<prefix>_battery_strings` | 2012 | uint16 | pcs | no | Battery Strings — Battery Strings |
| `sensor.<prefix>_battery_total_voltage` | 2024 | uint16 | V | no | Battery Total Voltage — Battery Total Voltage |
| `sensor.<prefix>_battery_total_current` | 2025 | uint16 | A | no | Battery Total Current — Battery Total Current |
| `sensor.<prefix>_cycle_times` | 2026 | uint16 |  | no | Cycle Times — Cycle Times |
| `sensor.<prefix>_router_ssid_RO` | 25000 | char x20 |  | no | Router SSID (RO) — Router SSID (RO) |
| `sensor.<prefix>_router_password_RO` | 25024 | char x20 |  | no | Router Password (RO) — Router Password (RO) |
| `sensor.<prefix>_router_encryption_RO` | 25064 | char x1 |  | no | Router Encryption (RO) — Router Encryption (RO) |
| `sensor.<prefix>_manufacturer_RO` | 25128 | char x4 |  | no | Manufacturer (RO) — Manufacturer (RO) |
| `sensor.<prefix>_operation_mode_RO` | 25243 | uint16 |  | no | Operation Mode (RO) — Operation Mode (RO) (6 state labels) |
| `sensor.<prefix>_batt_charge_curr_max_RO` | 25353 | uint16 | A | yes | Battery Charge Current Max (RO) — Battery Charge Current Max (RO) |
| `sensor.<prefix>_batt_discharge_curr_max_RO` | 25355 | uint16 | A | yes | Battery Discharge Current Max (RO) — Battery Discharge Current Max (RO) |
| `sensor.<prefix>_feed_power_para_RO` | 27510 | uint16 | W | no | Feed Power Para (RO) — Feed Power Para (RO) |
| `sensor.<prefix>_ems_power_mode_RO` | 27511 | uint16 |  | no | EMS Power Mode (RO) — EMS Power Mode (RO) (15 state labels) |
| `sensor.<prefix>_ems_power_set_RO` | 27512 | uint16 | W | no | EMS Power Set (RO) — EMS Power Set (RO) |

### binary_sensor — polled from Modbus

| Entity | Register | Type | Unit | Enabled | Description |
|---|---|---|---|---|---|
| `binary_sensor.<prefix>_bms_comm_ok` | 2002 | uint16 |  | no | BMS Communication OK — BMS Communication OK |

### select — writable

| Entity | Register | Type | Unit | Enabled | Description |
|---|---|---|---|---|---|
| `select.<prefix>_operation_mode` | 25243 |  |  | yes | Operation Mode — Operation Mode (options: self_use, off_grid, backup, tou, battery_priority, dynamic_trade) |
| `select.<prefix>_ems_power_mode` | 27511 |  |  | yes | EMS Power Mode — EMS Power Mode (options: stopped, auto, charge_pv, dischg_pv, import_ac, export_ac, conserve, off_grid, battery_standby, buy_power, sell_power, charge_bat, discharge_bat, charge_only_self_use, self_use) |
| `select.<prefix>_exit_mode_set` | 27548 |  |  | no | Exit Mode Set — Mode to return to when the EMS power mode expires (options: self_use, off_grid, backup, tou, battery_priority, ai_optimization, restore_previous) |

### switch — writable

| Entity | Register | Type | Unit | Enabled | Description |
|---|---|---|---|---|---|
| `switch.<prefix>_backup_function` | 25252 | uint16 |  | yes | Backup Function — Backup Function |

### number — writable

| Entity | Register | Type | Unit | Enabled | Description |
|---|---|---|---|---|---|
| `number.<prefix>_port_number_1` | 25100 | uint16 |  | no | Port Number 1 — Port Number 1 (range 1…65535; step 1) |
| `number.<prefix>_modbus_address` | 25127 | uint16 |  | no | Modbus Address — Modbus Address (range 1…247; step 1) |
| `number.<prefix>_modbus_baud_rate` | 25132 | uint32 x2 | baud | no | Modbus Baud Rate — Modbus Baud Rate (range 9600…115200; step 1) |
| `number.<prefix>_max_charge_current` | 25353 | uint16 | A | no | Max Charge Current — Max Charge Current (range 0…1000; step 1) |
| `number.<prefix>_max_discharge_current` | 25355 | uint16 | A | no | Max Discharge Current — Max Discharge Current (range 0…1000; step 1) |
| `number.<prefix>_charge_to_soc` | 25362 | uint16 | % | no | Charge to SoC — Charge to SoC (range 0…100; step 1) |
| `number.<prefix>_ems_power_set` | 27512 | int16 | W | yes | EMS Power Set — EMS Power Set (range -980…980; step 50) |
| `number.<prefix>_tou_start_time_1` | 27515 | uint16 |  | no | TOU Slot 1 Start Time (HHMM) — TOU slot 1 start time (HHMM); app=Time Slot (range 0…2359; step 1) |
| `number.<prefix>_tou_end_time_1` | 27516 | uint16 |  | no | TOU Slot 1 End Time (HHMM) — TOU slot 1 end time (HHMM); app=Time Slot (range 0…2359; step 1) |
| `number.<prefix>_tou_power_1` | 27517 | int16 | W | no | TOU Slot 1 Power — TOU slot 1 battery power in W (negative = charge); app=Power (range -980…980; step 1) |
| `number.<prefix>_tou_work_week_1` | 27518 | uint16 |  | no | TOU Slot 1 Work Week — TOU slot 1 weekday bitmask (0xFF00 / days) (range 0…65535; step 1) |
| `number.<prefix>_tou_start_time_2` | 27519 | uint16 |  | no | TOU Slot 2 Start Time (HHMM) — TOU slot 2 start time (HHMM); app=Time Slot (range 0…2359; step 1) |
| `number.<prefix>_tou_end_time_2` | 27520 | uint16 |  | no | TOU Slot 2 End Time (HHMM) — TOU slot 2 end time (HHMM); app=Time Slot (range 0…2359; step 1) |
| `number.<prefix>_tou_power_2` | 27521 | int16 | W | no | TOU Slot 2 Power — TOU slot 2 battery power in W (negative = charge); app=Power (range -980…980; step 1) |
| `number.<prefix>_tou_work_week_2` | 27522 | uint16 |  | no | TOU Slot 2 Work Week — TOU slot 2 weekday bitmask (0xFF00 / days) (range 0…65535; step 1) |
| `number.<prefix>_tou_start_time_3` | 27523 | uint16 |  | no | TOU Slot 3 Start Time (HHMM) — TOU slot 3 start time (HHMM); app=Time Slot (range 0…2359; step 1) |
| `number.<prefix>_tou_end_time_3` | 27524 | uint16 |  | no | TOU Slot 3 End Time (HHMM) — TOU slot 3 end time (HHMM); app=Time Slot (range 0…2359; step 1) |
| `number.<prefix>_tou_power_3` | 27525 | int16 | W | no | TOU Slot 3 Power — TOU slot 3 battery power in W (negative = charge); app=Power (range -980…980; step 1) |
| `number.<prefix>_tou_work_week_3` | 27526 | uint16 |  | no | TOU Slot 3 Work Week — TOU slot 3 weekday bitmask (0xFF00 / days) (range 0…65535; step 1) |
| `number.<prefix>_tou_start_time_4` | 27527 | uint16 |  | no | TOU Slot 4 Start Time (HHMM) — TOU slot 4 start time (HHMM); app=Time Slot (range 0…2359; step 1) |
| `number.<prefix>_tou_end_time_4` | 27528 | uint16 |  | no | TOU Slot 4 End Time (HHMM) — TOU slot 4 end time (HHMM); app=Time Slot (range 0…2359; step 1) |
| `number.<prefix>_tou_power_4` | 27529 | int16 | W | no | TOU Slot 4 Power — TOU slot 4 battery power in W (negative = charge); app=Power (range -980…980; step 1) |
| `number.<prefix>_tou_work_week_4` | 27530 | uint16 |  | no | TOU Slot 4 Work Week — TOU slot 4 weekday bitmask (0xFF00 / days) (range 0…65535; step 1) |
| `number.<prefix>_soc_force_charge_start` | 27531 | uint16 | % | no | Force Charge Start SoC — SOC at which forced charging starts (range 0…100; step 1) |
| `number.<prefix>_soc_force_charge_stop` | 27532 | uint16 | % | no | Force Charge Stop SoC — SOC at which forced charging stops (range 0…100; step 1) |
| `number.<prefix>_ems_power_mode_effective_time` | 27547 | uint16 | s | no | EMS Power Mode Effective Time — How long the EMS power mode stays active (0 = permanent) (range 0…65535; step 1) |

### button — action

| Entity | Register | Type | Unit | Enabled | Description |
|---|---|---|---|---|---|
| `button.<prefix>_start_ac_port_connection` | 25218 | uint16 |  | no | Start AC Port Connection — Start AC Port Connection |
| `button.<prefix>_stop_ac_port_connection` | 25219 | uint16 |  | no | Stop AC Port Connection — Stop AC Port Connection |
| `button.<prefix>_reset_inverter` | 25220 | uint16 |  | no | Reset Inverter — Reset Inverter |
| `button.<prefix>_clear_all_economic_mode` | 27533 | uint16 |  | no | Clear All Economic Mode — Clear all economic (TOU) mode schedules |

### sensor — computed

| Entity | Register | Type | Unit | Enabled | Description |
|---|---|---|---|---|---|
| `sensor.<prefix>_firmware_version` | computed |  |  | yes | Firmware Version —  |

### sensor — computed

| Entity | Register | Type | Unit | Enabled | Description |
|---|---|---|---|---|---|
| `sensor.<prefix>_round_trip_efficiency_total` | computed |  | % | yes | Round Trip Efficiency Total —  |

### sensor — computed

| Entity | Register | Type | Unit | Enabled | Description |
|---|---|---|---|---|---|
| `sensor.<prefix>_stored_energy` | computed |  | kWh | yes | Stored Energy —  |

### sensor — computed

| Entity | Register | Type | Unit | Enabled | Description |
|---|---|---|---|---|---|
| `sensor.<prefix>_battery_cycle_count_calc` | computed |  |  | yes | Cycle Count (Calc) —  |

### sensor — computed

| Entity | Register | Type | Unit | Enabled | Description |
|---|---|---|---|---|---|
| `sensor.<prefix>_tou_schedule_1` | computed |  |  | yes | TOU Schedule 1 —  |
| `sensor.<prefix>_tou_schedule_2` | computed |  |  | yes | TOU Schedule 2 —  |
| `sensor.<prefix>_tou_schedule_3` | computed |  |  | yes | TOU Schedule 3 —  |
| `sensor.<prefix>_tou_schedule_4` | computed |  |  | yes | TOU Schedule 4 —  |
