# Complete Setup Guide: Dyness Aquavolt + Home Battery Control (HBC)

## Overview

This guide walks you through:
1. Installing the Dyness Aquavolt Modbus integration in Home Assistant
2. Installing Home Battery Control (Node-RED based)
3. Creating the entity mapping between Dyness and HBC
4. Leaving hooks for future expansion/planning

---

## Part A: Install Dyness Aquavolt Modbus Integration

### A1. Copy Integration Files

Copy the `custom_components/dyness_modbus/` directory to your Home Assistant config:

```
/config/custom_components/dyness_modbus/
```

You can do this via:
- **Samba/SSH**: Copy from `c:\dev\dyeness_av\custom_components\dyness_modbus\`
- **HACS**: Once published to GitHub, install via HACS custom repository

### A2. Restart Home Assistant

After copying files, restart HA:
- **Settings → System → Restart**

### A3. Add the Integration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search: **Dyness Aquavolt Modbus**
3. Enter:
   - **IP Address**: your Modbus TCP gateway IP (e.g., `192.168.1.100`)
   - **Port**: `502`
   - **Unit ID**: `1`
4. Click **Submit**

### A4. Verify Entities

Check **Developer Tools → States** for:
- `sensor.dyness_aquavolt_battery_power`
- `sensor.dyness_aquavolt_bms_soc`
- `sensor.dyness_aquavolt_battery_voltage`
- `sensor.dyness_aquavolt_battery_current`
- `sensor.dyness_aquavolt_utility_p1_power`
- `sensor.dyness_aquavolt_ac_port_power_total`
- `binary_sensor.dyness_aquavolt_modbus_connection` (should be `on`)

### A5. Configure Polling (Optional)

**Settings → Devices & Services → Dyness Aquavolt Modbus → Configure**
- High priority: 10s (power, voltage, current, SOC, state)
- Low priority: 60s (totals, diagnostics, firmware)

---

## Part B: Install Home Battery Control (HBC)

### B1. Prerequisites

- Node-RED add-on installed in Home Assistant
- HACS installed
- A P1 meter sensor (grid power) available in HA

### B2. Install HBC Packages

1. Clone or download the HBC repository:
   ```
   https://github.com/gitcodebob/marstek-venus-rs485-node-red
   ```

2. Copy the package files to your HA config:
   ```
   /config/packages/house_battery_control.yaml
   /config/packages/house_battery_control_config.yaml
   ```

3. Verify `configuration.yaml` includes packages:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

4. Restart Home Assistant.

### B3. Import Node-RED Flows

1. Open Node-RED (usually `http://homeassistant.local:1880`)
2. Menu → **Import** → **Select a file to import**
3. Import these flows in order:
   - `node-red/00 master-switch-flow.json`
   - `node-red/01 start-flow.json`
   - `node-red/02 strategy-*.json` (choose your strategy)
   - `node-red/00 presets-switch-flow.json`

4. Deploy all flows.

### B4. Configure P1 Meter

In HBC, the P1 meter power sensor is required. Update the template in `house_battery_control_config.yaml`:

```yaml
template:
  - sensor:
      - name: "P1 Meter Power"
        unique_id: "p1_meter_power"
        state: "{{ states('sensor.dyness_aquavolt_utility_p1_power') | float(0) }}"
        unit_of_measurement: "W"
        device_class: "power"
        state_class: "measurement"
```

---

## Part C: Create Entity Mapping (Dyness → HBC)

HBC expects entities named `marstek_m1_*`. Create a mapping file.

### C1. Create Mapping Package

Create `/config/packages/dyness_hbc_mapping.yaml`:

```yaml
# Dyness Aquavolt → Home Battery Control entity mapping
# Maps Dyness entity names to the HBC-expected marstek_m1_* names

template:
  - sensor:
      # Battery power (HBC expects sensor.marstek_m1_battery_power)
      - name: "Marstek M1 Battery Power"
        unique_id: "marstek_m1_battery_power"
        state: "{{ states('sensor.dyness_aquavolt_battery_power') | float(0) }}"
        unit_of_measurement: "W"
        device_class: "power"
        state_class: "measurement"
        availability: "{{ is_number(states('sensor.dyness_aquavolt_battery_power')) }}"

      # Battery SOC (HBC expects sensor.marstek_m1_battery_soc)
      - name: "Marstek M1 Battery SOC"
        unique_id: "marstek_m1_battery_soc"
        state: "{{ states('sensor.dyness_aquavolt_bms_soc') | float(0) }}"
        unit_of_measurement: "%"
        device_class: "battery"
        state_class: "measurement"
        availability: "{{ is_number(states('sensor.dyness_aquavolt_bms_soc')) }}"

      # Battery current
      - name: "Marstek M1 Battery Current"
        unique_id: "marstek_m1_battery_current"
        state: "{{ states('sensor.dyness_aquavolt_battery_current') | float(0) }}"
        unit_of_measurement: "A"
        device_class: "current"
        state_class: "measurement"

      # Battery voltage
      - name: "Marstek M1 Battery Voltage"
        unique_id: "marstek_m1_battery_voltage"
        state: "{{ states('sensor.dyness_aquavolt_battery_voltage') | float(0) }}"
        unit_of_measurement: "V"
        device_class: "voltage"
        state_class: "measurement"

      # Inverter state
      - name: "Marstek M1 Inverter State"
        unique_id: "marstek_m1_inverter_state"
        state: "{{ states('sensor.dyness_aquavolt_inverter_state') }}"

      # Battery mode
      - name: "Marstek M1 Battery Mode"
        unique_id: "marstek_m1_battery_mode"
        state: "{{ states('sensor.dyness_aquavolt_battery_mode') }}"

      # Total battery charge energy
      - name: "Marstek M1 Total Charging Energy"
        unique_id: "marstek_m1_total_charging_energy"
        state: "{{ states('sensor.dyness_aquavolt_battery_charge_energy_total') | float(0) }}"
        unit_of_measurement: "kWh"
        device_class: "energy"
        state_class: "total_increasing"

      # Total battery discharge energy
      - name: "Marstek M1 Total Discharging Energy"
        unique_id: "marstek_m1_total_discharging_energy"
        state: "{{ states('sensor.dyness_aquavolt_battery_discharge_energy_total') | float(0) }}"
        unit_of_measurement: "kWh"
        device_class: "energy"
        state_class: "total_increasing"

      # P1 Meter Power (grid power for HBC)
      - name: "P1 Meter Power"
        unique_id: "p1_meter_power"
        state: "{{ states('sensor.dyness_aquavolt_utility_p1_power') | float(0) }}"
        unit_of_measurement: "W"
        device_class: "power"
        state_class: "measurement"
        availability: "{{ is_number(states('sensor.dyness_aquavolt_utility_p1_power')) }}"

      # AC Port Power
      - name: "AC Port Power"
        unique_id: "dyness_ac_port_power"
        state: "{{ states('sensor.dyness_aquavolt_ac_port_power_total') | float(0) }}"
        unit_of_measurement: "W"
        device_class: "power"
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
    icon: "mdi:battery-90"

  marstek_m1_discharging_cutoff_capacity:
    name: "Marstek M1 Discharging Cutoff Capacity"
    min: 11
    max: 80
    initial: 11
    step: 1
    unit_of_measurement: "%"
    mode: box
    icon: "mdi:battery-10"

input_select:
  # Map to Dyness operation mode select
  marstek_master_battery_mode:
    name: "Master Battery Mode"
    options:
      - "Manual control"
      - "Full control"
    icon: "mdi:battery-heart"
```

### C2. Restart Home Assistant

After adding the mapping file, restart HA to load the new entities.

### C3. Verify Mapping

Check **Developer Tools → States** for:
- `sensor.marstek_m1_battery_power`
- `sensor.marstek_m1_battery_soc`
- `sensor.p1_meter_power`
- `input_number.marstek_m1_charging_cutoff_capacity`

---

## Part D: Files to Add/Edit

### New Files to Create

| File | Location | Purpose |
|------|----------|---------|
| `dyness_hbc_mapping.yaml` | `/config/packages/` | Entity name mapping Dyness → HBC |
| `dyness_aquavolt_modbus.yaml` | `/config/packages/` | Optional: custom automations for Dyness |

### Files to Edit

| File | Change |
|------|--------|
| `/config/configuration.yaml` | Verify `packages: !include_dir_named packages` is present |
| `/config/packages/house_battery_control_config.yaml` | Set P1 meter power to `sensor.dyness_aquavolt_utility_p1_power` |
| `/config/custom_components/dyness_modbus/manifest.json` | Update `codeowners` with your GitHub username |

### Optional: Custom Automation Hooks

Create `/config/packages/dyness_hooks.yaml` for future integration:

```yaml
# Dyness Aquavolt - Custom Automation Hooks
# Add your own automations, scripts, and planning logic here

automation:
  # Example: Notify when battery is low
  - alias: "Dyness Low Battery Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.dyness_aquavolt_bms_soc
        below: 20
    action:
      - service: notify.persistent_notification
        data:
          title: "Dyness Battery Low"
          message: "Battery SOC is below 20%"

  # Example: Switch to backup mode on grid outage
  - alias: "Dyness Grid Loss → Backup"
    trigger:
      - platform: state
        entity_id: sensor.dyness_aquavolt_ac_port_mode
        to: "2"  # Fault mode
    action:
      - service: select.select_option
        target:
          entity_id: select.dyness_aquavolt_operation_mode
        data:
          option: "backup"

script:
  # Example: Force charge to 100%
  dyness_force_charge_full:
    alias: "Dyness Force Charge to Full"
    sequence:
      - service: select.select_option
        target:
          entity_id: select.dyness_aquavolt_operation_mode
        data:
          option: "self_use"
      - service: number.set_value
        target:
          entity_id: number.dyness_aquavolt_charge_to_soc
        data:
          value: 100
      - service: number.set_value
        target:
          entity_id: number.dyness_aquavolt_ems_power_set
        data:
          value: 3000

  # Example: Enter standby mode
  dyness_standby:
    alias: "Dyness Standby"
    sequence:
      - service: number.set_value
        target:
          entity_id: number.dyness_aquavolt_ems_power_set
        data:
          value: 0
      - service: select.select_option
        target:
          entity_id: select.dyness_aquavolt_operation_mode
        data:
          option: "self_use"

input_number:
  # Planning: target charge level for tomorrow
  dyness_target_charge_soc:
    name: "Dyness Target Charge SoC"
    min: 0
    max: 100
    step: 1
    initial: 80
    unit_of_measurement: "%"
    icon: "mdi:battery-charging"

  # Planning: max grid import power
  dyness_max_grid_import:
    name: "Dyness Max Grid Import Power"
    min: 0
    max: 10000
    step: 100
    initial: 3000
    unit_of_measurement: "W"
    icon: "mdi:transmission-tower-import"

input_boolean:
  # Planning: enable dynamic tariff charging
  dyness_dynamic_tariff_enabled:
    name: "Dyness Dynamic Tariff Charging"
    icon: "mdi:cash-multiple"

  # Planning: enable peak shaving
  dyness_peak_shaving_enabled:
    name: "Dyness Peak Shaving"
    icon: "mdi:home-import-outline"
```

---

## Part E: Hooks for Future DAO/Planning Integration

### E1. What are "hooks"?

Hooks are extension points in your configuration that allow future features (planning algorithms, DAO governance, dynamic tariffs) to integrate without modifying core files.

### E2. Available Hooks

| Hook Location | Purpose | How to Use |
|---------------|---------|------------|
| `/config/packages/dyness_hooks.yaml` | Custom automations, scripts, inputs | Add your own logic here |
| `dyness_hbc_mapping.yaml` | Entity name mapping | Add new mapped entities here |
| Node-RED flows | Control strategies | Import new strategy flows |
| `input_number.*` | Planning parameters | Adjust target levels, power limits |
| `input_boolean.*` | Feature toggles | Enable/disable features dynamically |
| `input_select.*` | Mode selection | Add new operation modes |

### E3. Planning Integration Points

The Dyness integration exposes these controllable entities for planning:

**Write targets (for planning algorithms):**
- `select.dyness_aquavolt_operation_mode` — Change operating mode
- `number.dyness_aquavolt_ems_power_set` — Set battery power (W)
- `number.dyness_aquavolt_charge_to_soc` — Set charge target (%)
- `number.dyness_aquavolt_max_charge_current` — Set max charge current (A)
- `number.dyness_aquavolt_max_discharge_current` — Set max discharge current (A)
- `switch.dyness_aquavolt_backup_function` — Enable/disable backup
- `button.dyness_aquavolt_reset_inverter` — Reset inverter

**Read sensors (for planning decisions):**
- `sensor.dyness_aquavolt_bms_soc` — Current battery level
- `sensor.dyness_aquavolt_battery_power` — Current battery power
- `sensor.dyness_aquavolt_utility_p1_power` — Grid power (P1)
- `sensor.dyness_aquavolt_ac_port_power_total` — AC port power
- `sensor.dyness_aquavolt_battery_charge_energy_total` — Total charged energy
- `sensor.dyness_aquavolt_battery_discharge_energy_total` — Total discharged energy
- `sensor.dyness_aquavolt_inverter_state` — Inverter state

### E4. Example Planning Script

Add to `/config/packages/dyness_hooks.yaml`:

```yaml
script:
  dyness_planning_charge_optimal:
    alias: "Dyness Planning: Optimal Charge"
    description: "Charge battery to target based on dynamic tariff"
    sequence:
      - variables:
          target_soc: "{{ states('input_number.dyness_target_charge_soc') | float(80) }}"
          current_soc: "{{ states('sensor.dyness_aquavolt_bms_soc') | float(0) }}"
          max_power: "{{ states('input_number.dyness_max_grid_import') | float(3000) }}"
      - if:
          - condition: template
            value_template: "{{ current_soc < target_soc }}"
        then:
          - service: select.select_option
            target:
              entity_id: select.dyness_aquavolt_operation_mode
            data:
              option: "self_use"
          - service: number.set_value
            target:
              entity_id: number.dyness_aquavolt_charge_to_soc
            data:
              value: "{{ target_soc }}"
          - service: number.set_value
            target:
              entity_id: number.dyness_aquavolt_ems_power_set
            data:
              value: "{{ max_power }}"
        else:
          - service: number.set_value
            target:
              entity_id: number.dyness_aquavolt_ems_power_set
            data:
              value: 0
```

### E5. Future DAO Integration Notes

If you plan to integrate a DAO (Distributed Autonomous Organization) or automated planning system:

1. **API Access**: Use HA's REST API to read sensors and call services:
   - GET `/api/states/sensor.dyness_aquavolt_bms_soc`
   - POST `/api/services/number/set_value` with `{"entity_id": "number.dyness_aquavolt_ems_power_set", "value": 3000}`

2. **WebSocket Events**: Subscribe to `state_changed` events for real-time battery data

3. **Webhook Triggers**: Create HA automations with webhook triggers to receive external planning commands:
   ```yaml
   automation:
     - alias: "Dyness DAO Command Receiver"
       trigger:
         - platform: webhook
           webhook_id: dyness_dao_command
       action:
         - service: "{{ trigger.json.service }}"
           target:
             entity_id: "{{ trigger.json.entity_id }}"
           data: "{{ trigger.json.data }}"
   ```

4. **Node-RED Integration**: The HBC Node-RED flows can be extended with new strategy nodes that call the Dyness write services.

---

## Summary: Quick Start Checklist

- [ ] Copy `custom_components/dyness_modbus/` to `/config/custom_components/`
- [ ] Restart Home Assistant
- [ ] Add Dyness Aquavolt Modbus integration via UI
- [ ] Verify entities appear in Developer Tools
- [ ] Install HBC packages (`house_battery_control.yaml`, `house_battery_control_config.yaml`)
- [ ] Import Node-RED flows
- [ ] Create `dyness_hbc_mapping.yaml` with template sensors
- [ ] Restart Home Assistant
- [ ] Verify `sensor.marstek_m1_battery_power` and `sensor.p1_meter_power` exist
- [ ] Configure HBC onboarding in dashboard
- [ ] Test charge/discharge via Node-RED flows
- [ ] (Optional) Add custom hooks in `dyness_hooks.yaml`