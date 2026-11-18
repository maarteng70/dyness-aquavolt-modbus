# Dyness Aquavolt Battery - Home Assistant Integration

This is a custom HACS-compatible integration for Dyness Aquavolt battery systems, using **Modbus TCP** via an RS485-to-WiFi gateway or direct Ethernet. No YAML required. The integration provides sensors, switches and number controls to monitor and manage the battery directly from Home Assistant.

### Requirements

- A configured **Modbus RTU to Modbus TCP bridge** connected to the inverter's EMS RS485 port
- Alternatively: Ethernet Connection to inverter with Modbus TCP support
- The IP address, port of the Modbus TCP (usually port 502) and Unit ID (also called Slave ID, default 1).
- Home Assistant Core 2025.9 or later
- HACS installed

### Features

- Native Modbus TCP polling via HA's built-in Modbus integration (no separate pymodbus dependency)
- Polling is handled centrally via the DataUpdateCoordinator with dynamic intervals per entity type
- Smart contiguous block polling groups adjacent registers into single Modbus requests where possible, with automatic fallback to per-entity reads on failure
- Configurable scan intervals via the integration options UI
- Fully asynchronous operation for optimal performance and responsiveness
- Sensors for battery voltage, current, SOC, power, energy, and fault/alarm status
- **AC Port** measurement point (inverter AC output) monitoring
- Utility P1 measure point (grid supply side) monitoring
- Diagnostic entities for communication health, firmware version, and BMS status
- Switches for backup function control
- Adjustable charge/discharge current and charge-to-SOC limits
- EMS power mode control
- Reset button for inverter reset
- Calculated sensors: round-trip efficiency, stored energy, cycle count
- UI-based configuration (Config Flow)
- Fully local, no cloud required

### Installation

1. Add this repository to HACS **Integrations → Custom repositories**
2. Install the "Dyness Aquavolt Modbus" integration
3. Restart Home Assistant
4. Add the integration via **Settings → Devices & Services**
5. Enter the connection details:
   - IP address of your Modbus TCP gateway
   - Port (default: 502)
   - Unit ID / Slave ID (default: 1, valid range: 1-255)

### Configuration

#### Polling Intervals

The integration uses intelligent polling with configurable intervals per entity type.

**Configurable via Options UI:**
- **High priority** (default: 10 seconds) - Fast-changing sensors such as power, voltage, current, SOC and state entities
- **Low priority** (default: 60 seconds) - Slower-changing sensors such as totals, diagnostics, firmware and device information

### Modbus Registers Used

Register definitions live in `custom_components/dyness_modbus/registers/dyness.yaml`.

Key register groups:
- **100-200**: PV, AC Port, Battery running data, Energy counters
- **213-214**: Battery SOC, Operate Mode
- **262-278**: Utility P1 measure point (grid supply side)
- **2000-2026**: BMS information
- **25200-25522**: Operation mode and system settings (RW)
- **25350-25363**: Battery parameters (RW)
- **27500-27548**: EMS manage data (RW)

### Home Battery Control (Node-RED) Compatibility

The `marstek-venus-rs485-node-red` project (Home Battery Control) reads from Home Assistant entities via Node-RED WebSocket nodes. It expects specific entity names from the Marstek/Fonske ecosystem. To use this Dyness integration with Home Battery Control, create **template sensors** in your Home Assistant `configuration.yaml` (or a package) that map Dyness entity names to the expected HBC names.

Add this to your configuration:

```yaml
template:
  # Battery power (maps Dyness battery_power to HBC expected name)
  - sensor:
      - name: "Marstek M1 Battery Power"
        unique_id: "marstek_m1_battery_power"
        state: "{{ states('sensor.dyness_aquavolt_battery_power') | float(0) }}"
        unit_of_measurement: "W"
        device_class: "power"
        state_class: "measurement"
        availability: "{{ is_number(states('sensor.dyness_aquavolt_battery_power')) }}"

  # Battery SOC (maps Dyness BMS SoC to HBC expected name)
  - sensor:
      - name: "Marstek M1 Battery SOC"
        unique_id: "marstek_m1_battery_soc"
        state: "{{ states('sensor.dyness_aquavolt_bms_soc') | float(0) }}"
        unit_of_measurement: "%"
        device_class: "battery"
        state_class: "measurement"
        availability: "{{ is_number(states('sensor.dyness_aquavolt_bms_soc')) }}"

  # AC Port / Grid supply power (Utility P1 measure point)
  - sensor:
      - name: "P1 Meter Power"
        unique_id: "p1_meter_power"
        state: "{{ states('sensor.dyness_aquavolt_utility_p1_power') | float(0) }}"
        unit_of_measurement: "W"
        device_class: "power"
        state_class: "measurement"
        availability: "{{ is_number(states('sensor.dyness_aquavolt_utility_p1_power')) }}"

  # AC Port Voltage (R phase)
  - sensor:
      - name: "AC Port Voltage"
        unique_id: "dyness_ac_port_voltage_r"
        state: "{{ states('sensor.dyness_aquavolt_ac_port_voltage_r') | float(0) }}"
        unit_of_measurement: "V"
        device_class: "voltage"
        state_class: "measurement"

  # Inverter state
  - sensor:
      - name: "Marstek M1 Inverter State"
        unique_id: "marstek_m1_inverter_state"
        state: "{{ states('sensor.dyness_aquavolt_inverter_state') }}"
        icon: "mdi:state-machine"

  # Battery current
  - sensor:
      - name: "Marstek M1 Battery Current"
        unique_id: "marstek_m1_battery_current"
        state: "{{ states('sensor.dyness_aquavolt_battery_current') | float(0) }}"
        unit_of_measurement: "A"
        device_class: "current"
        state_class: "measurement"

  # Battery voltage
  - sensor:
      - name: "Marstek M1 Battery Voltage"
        unique_id: "marstek_m1_battery_voltage"
        state: "{{ states('sensor.dyness_aquavolt_battery_voltage') | float(0) }}"
        unit_of_measurement: "V"
        device_class: "voltage"
        state_class: "measurement"

input_number:
  # Map to Dyness charge-to-SOC number
  marstek_m1_charging_cutoff_capacity:
    name: "Marstek M1 Charging Cutoff Capacity"
    min: 80
    max: 100
    initial: 100
    step: 1
    unit_of_measurement: "%"
    mode: box

  marstek_m1_discharging_cutoff_capacity:
    name: "Marstek M1 Discharging Cutoff Capacity"
    min: 11
    max: 80
    initial: 11
    step: 1
    unit_of_measurement: "%"
    mode: box

input_select:
  # Map to Dyness operation mode select
  marstek_master_battery_mode:
    name: "Master Battery Mode"
    options:
      - "Manual control"
      - "Full control"
    icon: "mdi:battery-heart"
```

### Entity Naming Convention

This integration intentionally avoids the word "grid" for the inverter AC connection point, using **AC Port** instead:

| Entity | Register | Purpose |
|--------|----------|---------|
| `sensor.dyness_aquavolt_ac_port_voltage_r` | 117 | AC Port Voltage (R phase) |
| `sensor.dyness_aquavolt_ac_port_current_r` | 118 | AC Port Current (R phase) |
| `sensor.dyness_aquavolt_ac_port_frequency_r` | 119 | AC Port Frequency (R phase) |
| `sensor.dyness_aquavolt_ac_port_power_r` | 120 | AC Port Power (R phase) |
| `sensor.dyness_aquavolt_ac_port_power_total` | 133 | Total AC Active Power |
| `sensor.dyness_aquavolt_ac_port_mode` | 132 | AC Port / Grid Mode |

The **Utility P1** measure point (registers 266-278) remains named "Utility P1" as it is the utility/smart-meter supply side, distinct from the inverter's AC Port.

### Notes

- Register addresses are based on the Dyness Hybrid Inverter Modbus Protocol V1.15
- All register addresses are decimal
- Scaling: real value = raw value / Mult (e.g., voltage with Mult 10 means raw 2305 = 230.5 V)
- `battery_total_voltage` (reg 2024) is marked **experimental** — it reports Volts only, not kWh capacity. The `stored_energy` calculated sensor using it is approximate.
- `battery_cycle_count_calc` now uses only discharge energy (no capacity reference).
- The integration supports Modbus TCP via RS485-to-TCP gateway
- For access to registers in the 42000+ range (if applicable), the inverter must be set to RS485 control mode
- Schedule Time format: start and end are entered as HHMM 24-hour integers
