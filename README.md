# Dyness Aquavolt Battery - Home Assistant Integration

#BURNS YOUR HOUSE DOWN 
This software can and will burn your house down. it is pre-release stuff. 


This is a custom HACS-compatible/Marketplace integration for Dyness Aquavolt battery systems, using **Modbus TCP** via an RS485-to-WiFi gateway or direct Ethernet. No YAML required. The integration provides sensors, switches and number controls to monitor and manage the battery directly from Home Assistant.

### Requirements

- A configured **Modbus RTU to Modbus TCP bridge** connected to the inverter's EMS RS485 port, eg, a ew41
- connect that bridge, it needs power and pin 5,6 from the rs485 interface. 

- The IP address, port of the Modbus TCP (usually port 502) and Unit ID (also called Slave ID, default 1).
- Home Assistant Core 2025.9 or later
- HACS installed in HA

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

1. Add this repository to HACS **Integrations → Custom repositories** Or add it to marketplace 
2. Install the "Dyness Aquavolt Modbus" integration https://github.com/maarteng70/dyness-aquavolt-modbus
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
- **High priority** (default: 5 seconds) - Fast-changing sensors : power
- **medium priority**, voltage, current, SOC and state entities
- **Low priority** (default: 60 seconds) - Slower-changing sensors such as totals, diagnostics, firmware and device information

### Modbus Registers Used

Register definitions live in `custom_components/dyness_modbus/registers/dyness.yaml`.

Key register groups:
- **100-200**: PV, AC Port, Battery running data, Energy counters
- **213-214**: Battery SOC, Operate Mode
- **262-278**: Utility measure point (grid supply side)
- **2000-2026**: BMS information
- **25200-25522**: Operation mode and system settings (RW)
- **25350-25363**: Battery parameters (RW)
- **27500-27548**: EMS manage data (RW)

### Power Ratio Handling

The Dyness inverter reports power registers (120, 125, 130, 133, 135, 137, etc.) as 4-byte values where:
- The **first 2 bytes** (first register) are ignored
- The **second 2 bytes** (second register) contain the signed power value

These registers use the custom `power_ratio` data type. Actual power = register value × Power Ratio coefficient (register 43). With ratio 1, the raw int16 value is returned directly.

### Phase Naming

AC Port and Utility phases are named **Phase 1, Phase 2, Phase 3** (not R, S, T).


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
- The integration supports Modbus TCP via RS485-to-TCP gateway you need to get such a device seperate, ew41 or lilygo comes to mind. 

