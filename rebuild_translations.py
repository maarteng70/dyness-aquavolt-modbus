import json

# Build the translation object from scratch
t = {
  "config": {
    "step": {
      "user": {
        "title": "Connect to Dyness Aquavolt Modbus",
        "description": "Enter the Modbus TCP connection details",
        "data": {
          "host": "IP Address",
          "port": "Port",
          "unit_id": "Unit ID"
        }
      }
    },
    "error": {
      "permission_denied": "Permission denied",
      "connection_refused": "Connection refused",
      "timed_out": "Connection timed out",
      "invalid_host": "Invalid host or IP address",
      "invalid_unit_id": "Invalid Modbus Unit ID (must be 1-255)",
      "unit_id_no_response": "No response from Unit ID. Check if the device uses this Unit ID",
      "cannot_connect": "Cannot connect to the device"
    },
    "abort": {
      "already_configured": "This device is already configured"
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Configure sensor scan intervals",
        "description": "Adjust polling frequency per category",
        "data": {
          "unit_id": "Modbus Unit ID"
        }
      },
      "menu": {
        "title": "Dyness options",
        "description": "Choose which settings to configure",
        "menu_options": {
          "connection": "Connection settings",
          "polling": "Polling intervals"
        }
      },
      "polling": {
        "title": "Configure polling intervals",
        "description": "Adjust polling frequency per category",
        "data": {
          "high": "High priority interval (s)",
          "low": "Low priority interval (s)"
        }
      },
      "connection": {
        "title": "Edit connection details",
        "description": "Change the Modbus TCP host, port and unit ID",
        "data": {
          "host": "IP Address",
          "port": "Port",
          "unit_id": "Unit ID"
        }
      }
    },
  "entity": {
    "sensor": {
      "modbus_protocol_version": { "name": "Modbus Protocol Version" },
      "rated_power": { "name": "Rated Power" },
      "ac_output_type": { "name": "AC Output Type" },
      "serial_number": { "name": "Serial Number" },
      "dsp1_software_version": { "name": "DSP1 Software Version" },
      "dsp2_software_version": { "name": "DSP2 Software Version" },
      "arm_software_version": { "name": "ARM Software Version" },
      "dsp_internal_firmware": { "name": "DSP Internal Firmware" },
      "arm_internal_firmware": { "name": "ARM Internal Firmware" },
      "device_hardware_version": { "name": "Device Hardware Version" },
      "manufacture": { "name": "Manufacturer" },
      "power_ratio": { "name": "Power Ratio" },
      "bms_version": { "name": "BMS Version" },
      "ac_port_voltage_phase1": { "name": "AC Port Voltage (Phase 1)" },
      "ac_port_current_phase1": { "name": "AC Port Current (Phase 1)" },
      "ac_port_frequency_phase1": { "name": "AC Port Frequency (Phase 1)" },
      "ac_port_power_phase1": { "name": "AC Port Power (Phase 1)" },
      "ac_port_power_total": { "name": "AC Active Power" },
      "ac_port_backup_power": { "name": "AC Port Backup Power" },
      "ac_port_reactive_power": { "name": "AC Reactive Power" },
      "ac_port_apparent_power": { "name": "AC Apparent Power" },
      "ac_port_mode": { "name": "AC Port Mode" },
      "ac_port_voltage_phase2": { "name": "AC Port Voltage (Phase 2)" },
      "ac_port_current_phase2": { "name": "AC Port Current (Phase 2)" },
      "ac_port_frequency_phase2": { "name": "AC Port Frequency (Phase 2)" },
      "ac_port_power_phase2": { "name": "AC Port Power (Phase 2)" },
      "ac_port_voltage_phase3": { "name": "AC Port Voltage (Phase 3)" },
      "ac_port_current_phase3": { "name": "AC Port Current (Phase 3)" },
      "ac_port_frequency_phase3": { "name": "AC Port Frequency (Phase 3)" },
      "ac_port_power_phase3": { "name": "AC Port Power (Phase 3)" },
      "battery_voltage": { "name": "Battery Voltage" },
      "battery_current": { "name": "Battery Current" },
      "battery_power": { "name": "Battery Power" },
      "battery_mode": { "name": "Battery Mode" },
      "inverter_state": { "name": "Inverter State" },
      "warning_code": { "name": "Warning Code" },
      "safety_country": { "name": "Safety Country" },
      "pv_energy_total": { "name": "PV Energy Total" },
      "pv_energy_day": { "name": "PV Energy Today" },
      "energy_to_grid_total": { "name": "Energy to Grid Total" },
      "energy_to_grid_day": { "name": "Energy to Grid Today" },
      "energy_from_grid_total": { "name": "Energy from Grid Total" },
      "energy_from_grid_day": { "name": "Energy from Grid Today" },
      "load_energy_total": { "name": "Load Energy Total" },
      "load_energy_day": { "name": "Load Energy Today" },
      "battery_charge_energy_total": { "name": "Battery Charge Energy Total" },
      "battery_charge_energy_day": { "name": "Battery Charge Energy Today" },
      "battery_discharge_energy_total": { "name": "Battery Discharge Energy Total" },
      "battery_discharge_energy_day": { "name": "Battery Discharge Energy Today" },
      "cpld_code": { "name": "CPLD Code" },
      "battery_voltage_2": { "name": "Battery 2 Voltage" },
      "battery_current_2": { "name": "Battery 2 Current" },
      "battery_power_2": { "name": "Battery 2 Power" },
      "battery_mode_2": { "name": "Battery 2 Mode" },
      "utility_voltage_phase1": { "name": "Utility Voltage (Phase 1)" },
      "utility_current_phase1": { "name": "Utility Current (Phase 1)" },
      "utility_power_phase1": { "name": "Utility Power (Phase 1)" },
      "utility_voltage_phase2": { "name": "Utility Voltage (Phase 2)" },
      "utility_current_phase2": { "name": "Utility Current (Phase 2)" },
      "utility_power_phase2": { "name": "Utility Power (Phase 2)" },
      "utility_voltage_phase3": { "name": "Utility Voltage (Phase 3)" },
      "utility_current_phase3": { "name": "Utility Current (Phase 3)" },
      "utility_power_phase3": { "name": "Utility Power (Phase 3)" },
      "utility_frequency": { "name": "Utility Frequency" },
      "total_utility_power": { "name": "Total Utility Power" },
      "bms_comm_status": { "name": "BMS Communication Status" },
      "bms_soc": { "name": "BMS SoC" },
      "bms_soh": { "name": "BMS SoH" },
      "battery_strings": { "name": "Battery Strings" },
      "battery_total_voltage": { "name": "Battery Total Voltage" },
      "battery_total_current": { "name": "Battery Total Current" },
      "cycle_times": { "name": "Cycle Times" },
      "firmware_version": { "name": "Firmware Version" },
      "round_trip_efficiency_total": { "name": "Round Trip Efficiency Total" },
      "stored_energy": { "name": "Stored Energy" },
      "solar_power_total": { "name": "Solar Power" },
      "battery_cycle_count_calc": { "name": "Cycle Count (Calc)" },
      "ems_power_set_RO": { "name": "EMS Power Set (RO)" },
      "ems_power_mode_RO": { "name": "EMS Power Mode (RO)", "state": {
          "255": "Stopped",
          "1": "Auto",
          "2": "Charge PV",
          "3": "Discharge + PV",
          "4": "Import AC",
          "5": "Export AC",
          "6": "Conserve",
          "7": "Off Grid",
          "8": "Battery Standby",
          "9": "Buy Power",
          "10": "Sell Power",
          "11": "Charge-BAT",
          "12": "Discharge-BAT"
        }
      },
      "operation_mode_RO": { "name": "Operation Mode (RO)", "state": {
          "0": "Self Use",
          "1": "Off Grid",
          "2": "Backup",
          "3": "Time of Use",
          "6": "Battery Priority",
          "7": "Dynamic Trade"
        }
      },
      "feed_power_para_RO": { "name": "Feed Power Para (RO)" },
      "batt_charge_curr_max_RO": { "name": "Battery Charge Current Max (RO)" },
      "batt_discharge_curr_max_RO": { "name": "Battery Discharge Current Max (RO)" },
      "router_ssid_RO": { "name": "Router SSID (RO)" },
      "router_password_RO": { "name": "Router Password (RO)" },
      "router_encryption_RO": { "name": "Router Encryption (RO)" },
      "manufacturer_RO": { "name": "Manufacturer (RO)" }
    },
    "binary_sensor": {
      "modbus_connection": { "name": "Modbus Connection" },
      "bms_comm_ok": { "name": "BMS Communication OK" }
    },
    "select": {
      "operation_mode": {
        "name": "Operation Mode",
        "state": {
          "self_use": "Self Use",
          "off_grid": "Off Grid",
          "backup": "Backup",
          "tou": "Time of Use",
          "battery_priority": "Battery Priority",
          "dynamic_trade": "Dynamic Trade"
        }
      },
      "ems_power_mode": {
        "name": "EMS Power Mode",
        "state": {
          "stopped": "Stopped",
          "auto": "Auto",
          "charge_pv": "Charge PV",
          "dischg_pv": "Discharge + PV",
          "import_ac": "Import AC",
          "export_ac": "Export AC",
          "conserve": "Conserve",
          "off_grid": "Off Grid",
          "battery_standby": "Battery Standby",
          "buy_power": "Buy Power",
          "sell_power": "Sell Power",
          "charge_bat": "Charge-BAT",
          "discharge_bat": "Discharge-BAT"
        }
      }
    },
    "switch": {
      "backup_function": { "name": "Backup Function" }
    },
    "number": {
      "max_charge_current": { "name": "Max Charge Current" },
      "max_discharge_current": { "name": "Max Discharge Current" },
      "charge_to_soc": { "name": "Charge to SoC" },
      "ems_power_set": { "name": "EMS Power Set" },
      "port_number_1": { "name": "Port Number 1" },
      "modbus_address": { "name": "Modbus Address" },
      "modbus_baud_rate": { "name": "Modbus Baud Rate" }
    },
    "button": {
      "reset_inverter": { "name": "Reset Inverter" },
      "start_ac_port_connection": { "name": "Start AC Port Connection" },
      "stop_ac_port_connection": { "name": "Stop AC Port Connection" }
    }
  }
}