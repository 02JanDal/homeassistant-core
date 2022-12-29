"""Constants for the SunGrow integration."""
import logging
from datetime import timedelta
from typing import List

LOGGER = logging.getLogger(__package__)

DOMAIN = "sungrow"
DEFAULT_NAME = "Sungrow"

KEY_COORDINATOR = "coordinator"
KEY_DEVICE_INFO = "device_info"
KEY_BATTERY_INFO = "battery_info"

SCAN_INTERVAL = timedelta(seconds=10)

BATTERY_DEVICE_VARIABLES: List[str] = [
    "battery_voltage",
    "battery_current",
    "battery_power",
    "battery_level",
    "battery_health",
    "battery_temperature",
    "daily_battery_discharge_energy",
    "total_battery_discharge_energy",
    "battery_capacity",
    "battery_maintenance",
    "battery_type",
    "battery_nominal_voltage",
    "charge_discharge",
    "charge_discharge_command",
    "max_soc",
    "min_soc",
    "reserved_soc_for_backup",
    "battery_over_voltage_threshold",
    "battery_under_voltage_threshold",
    "battery_over_temperature_threshold",
    "battery_under_temperature_threshold"
]
