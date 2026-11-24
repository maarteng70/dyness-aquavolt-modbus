# Release Notes: v2026.11.5

## Dyness Aquavolt Modbus - Home Assistant Integration

### Changes in v2026.11.5

#### Bug Fixes
- **Power registers changed from S32 to S16**: The Dyness inverter reports power registers (120, 125, 130, 133, 135, 137, 143, 268, 272, 276, 385) as 4-byte values where the first 2 bytes are ignored. The actual power value is in the second register as a signed int16. Previous versions decoded these as int32, producing incorrect values (e.g., 196608W instead of 3W).
- Removed duplicate/broken entries: `ems_power_set_RO`, `lock_in_power_RO`, `lock_out_power_RO`

#### New Features
- **AC Port phase naming**: Registers renamed from R/S/T to Phase 1/2/3 (e.g., `ac_port_power_phase1`, `ac_port_power_phase2`, `ac_port_power_phase3`)
- **Utility phase naming**: Same phase renaming for utility measure point (`utility_power_phase1`, `utility_power_phase2`, `utility_power_phase3`)
- **EMS Power Mode select** (register 27511): Full EMS control with Charge-BAT (0x000B) and Discharge-BAT (0x000C) modes
- **EMS Power Set number** (register 27512): Set power in Watts for Charge-BAT/Discharge-BAT modes
- **Read-only debug sensors** (disabled by default):
  - `ems_power_set_RO` (reg 27512) — raw EMS power setpoint
  - `ems_power_mode_RO` (reg 27511) — actual EMS power mode running
  - `operation_mode_RO` (reg 25243) — actual operation mode running
  - `feed_power_para_RO` (reg 27510) — active feed/export power limit
  - `batt_charge_curr_max_RO` (reg 25353) — active charge current limit
  - `batt_discharge_curr_max_RO` (reg 25355) — active discharge current limit
  - `router_ssid_RO`, `router_password_RO`, `router_encryption_RO`, `manufacturer_RO` — diagnostic (experimental)
- **Temperature/BUS sensors** added: `internal_temperature`, `radiator_temperature`, `module_temperature`, `bus_voltage`, `nbus_voltage`, `function_bit_value`
- **RW config numbers**: `port_number_1` (25100), `modbus_address` (25127), `modbus_baud_rate` (25132)
- **Power control numbers**: `max_charge_power` (25352), `max_discharge_power` (25355)
- **Safety Country sensor** (register 175) with full state mapping (Table 8-21, 107 country codes)
- **Template sensors** for Home Battery Control (Node-RED) compatibility documented in README

#### Configuration Changes
- `backup_function` switch now enabled by default
- `ems_power_mode` select now enabled by default
- `ems_power_set` number now enabled by default
- `max_charge_current` and `max_discharge_current` numbers disabled by default
- `cycle_times` sensor disabled by default (register timed out in testing)
- `battery_total_voltage` marked as experimental (diagnostic category)
- `cycle_count_calc` removed incorrect capacity reference

#### Documentation
- Added comprehensive `README.md` with installation, configuration, and register documentation
- Added `SETUP_GUIDE.md` with Home Battery Control integration instructions
- Added `RUNBOOK.md` with installation and GitHub publishing instructions
- Added template sensor YAML for HBC entity name mapping
- Added hooks for future DAO/planning integration

#### Removed
- `pymodbus` from `requirements.txt` (HA provides it)
- `power_ratio` custom data type from YAML (now using `int16` for power registers)
- "grid" naming for AC port entities (replaced with "ac_port")

---

## Compatibility

- **Home Assistant**: Core 2025.9+
- **HACS**: Compatible
- **Home Battery Control (Node-RED)**: Requires entity name mapping via template sensors (see README)

## Upgrade Notes

1. Replace `custom_components/dyness_modbus/` with the new version
2. Restart Home Assistant
3. Enable new entities via Settings → Devices & Services → Entities
4. Old entity names (`grid_*`, `utility_p1_*`, etc.) will be replaced by new names (`ac_port_*`, `utility_*_phase1`, etc.) — you may need to update automations/dashboards
5. The `power_ratio` data type is still available in `modbus_client.py` but is no longer used by the integration YAML

## Known Issues

- RW config registers (25000-25132) may time out on some inverter firmware versions — marked as experimental/disabled by default
- `cycle_times` register (2026) may time out on some firmware versions — disabled by default
- `battery_total_voltage` reports Volts only, not kWh capacity — stored energy calculation is approximate