"""The SunGrow integration."""
from __future__ import annotations

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_HOST, CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryError
from homeassistant.helpers.entity import DeviceInfo
from pysungrow import identify, SungrowClient
from pysungrow.identify import NotASungrowDeviceException

from .const import DOMAIN, KEY_COORDINATOR, KEY_DEVICE_INFO, KEY_BATTERY_INFO
from .coordinator import SungrowCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.SELECT, Platform.TEXT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SunGrow from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    host = entry.data[CONF_HOST]
    device_name = entry.data[CONF_DEVICE]

    client = AsyncModbusTcpClient(host, port=502)
    try:
        serial_number, device, output_type = await identify(client, slave=1)
    except NotASungrowDeviceException as err:
        raise ConfigEntryError from err
    except ModbusException as err:
        raise ConfigEntryNotReady from err

    if device.name != device_name:
        raise ConfigEntryError("Wrong inverter model")

    sungrow_client = SungrowClient(client, device, output_type, slave=1)
    # fetch software versions
    await sungrow_client.refresh(["arm_software_version", "dsp_software_version", "battery_type"])

    arm_version = await sungrow_client.get("arm_software_version")
    dsp_version = await sungrow_client.get("dsp_software_version")
    device_info = DeviceInfo(
        identifiers={(DOMAIN, serial_number)},
        name=device_name,
        manufacturer="Sungrow",
        model=device.name,
        sw_version=f"{arm_version}\n{dsp_version}" if arm_version and dsp_version else None
    )

    battery_type = await sungrow_client.get("battery_type") if "battery_type" in sungrow_client.keys else None
    battery_info = DeviceInfo(
        identifiers={(DOMAIN, serial_number + "-battery")},
        name=f"{device_name} Battery", # TODO: translate
        via_device=(DOMAIN, serial_number),
        manufacturer=battery_type.manufacturer if battery_type else None
    )

    coordinator = SungrowCoordinator(hass, serial_number, sungrow_client)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        KEY_COORDINATOR: coordinator,
        KEY_DEVICE_INFO: device_info,
        KEY_BATTERY_INFO: battery_info
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
