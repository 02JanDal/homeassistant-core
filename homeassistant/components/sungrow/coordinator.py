from typing import Optional, Any

import async_timeout
from pymodbus.exceptions import ModbusException

from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sungrow.const import (
    LOGGER,
    DOMAIN,
    BATTERY_DEVICE_VARIABLES,
    SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
    CoordinatorEntity,
)
from pysungrow import SungrowClient
from pysungrow.definitions.variable import VariableDefinition


class SungrowCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, serial_number: str, client: SungrowClient):
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}-{serial_number}",
            update_interval=SCAN_INTERVAL,
        )
        self._client = client
        self._serial_number = serial_number
        self._last_update_was_successful = False

    @property
    def serial_number(self) -> str:
        return self._serial_number

    @property
    def client(self) -> SungrowClient:
        return self._client

    @property
    def last_update_was_successful(self) -> bool:
        return self._last_update_was_successful

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(5):
                await self._client.refresh()
                self._last_update_was_successful = True
                return self._client.data
        except ModbusException as err:
            self._last_update_was_successful = False
            raise UpdateFailed(f"Error communicating with inverter: {err}")


class SungrowCoordinatorEntity(CoordinatorEntity[SungrowCoordinator]):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SungrowCoordinator,
        device_info: DeviceInfo,
        description: EntityDescription,
    ):
        super().__init__(coordinator)
        self._attr_device_info = device_info
        self._attr_unique_id = f"{DOMAIN}-{coordinator.serial_number}-{description.key}"
        self.entity_description = description

    @property
    def variable(self) -> VariableDefinition:
        return self.coordinator.client.variable(self.entity_description.key)

    @property
    def name(self) -> Optional[str]:
        if self.entity_description.name is not None:
            return self.entity_description.name
        name = self.entity_description.key
        if self.entity_description.key in BATTERY_DEVICE_VARIABLES:
            name = name.replace("battery_", "")
        name = name.replace("_", " ").title()
        name = (
            name.replace("Dc", "DC")
            .replace("Arm", "ARM")
            .replace("Dsp", "DSP")
            .replace("Mppt", "MPPT")
            .replace("Drm", "DRM")
            .replace("Pv", "PV")
        )
        return name

    @property
    def device_class(self) -> Optional[str]:
        if self.entity_description.device_class:
            return self.entity_description.device_class
        if not issubclass(self.__class__, (SensorEntity, NumberEntity)):
            return super().device_class

        if self.variable.unit == "A":
            return "current"
        elif self.variable.unit in ("h", "min", "s"):
            return "duration"
        elif self.variable.unit in ("Wh", "kWh"):
            return "energy"
        elif self.variable.unit == "Hz":
            return "frequency"
        elif self.variable.unit in ("W", "kW"):
            return "power"
        elif self.variable.unit == "var":
            return "reactive_power"
        elif self.variable.unit == "°C":
            return "temperature"
        elif self.variable.unit == "V":
            return "voltage"
        elif self.variable.unit == "kg":
            return "weight"
        return super().device_class

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_was_successful

    @property
    def data(self):
        return self.coordinator.data[self.entity_description.key]

    async def set_data(self, value: Any):
        await self.coordinator.client.set(self.entity_description.key, value)
        await self.coordinator.async_request_refresh()
