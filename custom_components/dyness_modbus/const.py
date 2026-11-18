# Integration domain name
DOMAIN = "dyness_modbus"

# Manufacturer and model information for the Dyness Aquavolt hybrid inverter
MANUFACTURER = "Dyness"
MODEL = "Aquavolt"

# Default network configuration for Modbus TCP connection
DEFAULT_PORT = 502
DEFAULT_MESSAGE_WAIT_MS = 80  # Default wait time for Modbus messages in milliseconds
DEFAULT_UNIT_ID = 1  # Default Modbus Unit ID (slave ID), factory default is 01H

# General scan intervals (in seconds)
DEFAULT_SCAN_INTERVALS = {
    "high": 10,      # fast-changing sensors (power, voltage, current, SOC, state)
    "low": 60,       # slower-changing sensors (energy totals, diagnostics, firmware)
}

# Supported device versions (single model for Aquavolt)
SUPPORTED_VERSIONS = [
    "Aquavolt",
]

# Register address map from Dyness Hybrid Inverter Modbus Protocol V1.15
# All addresses are decimal as per the protocol specification.
#
# Key register groups:
#   170-172   Battery 1 voltage/current/power
#   213       Battery SOC
#   173       Battery work mode
#   176       Inverter work state
#   117-119   Grid R phase voltage/current/frequency
#   133       AC active power (S32, 2 regs)
#   195-200   Battery charge/discharge energy counters
#   2026      Cycle times
#   266-278   Utility P1 measure point (voltage/current/power/frequency)
#   25243     Operation mode set (RW)
#   25252     Backup function enable (RW)
#   25352-25363 Battery parameters (RW)
#   27511-27512 EMS power mode/set (RW)
