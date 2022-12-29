from datetime import time
from time import strptime
from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.text import TextEntityDescription, TextEntity

from .const import (
    DOMAIN,
    KEY_COORDINATOR,
    KEY_DEVICE_INFO,
    KEY_BATTERY_INFO,
    BATTERY_DEVICE_VARIABLES,
)
from .coordinator import SungrowCoordinator, SungrowCoordinatorEntity

TIME_PATTERN = "[0-9]{2}:[0-9]{2}"

DESCRIPTIONS: tuple[TextEntityDescription, ...] = (
    TextEntityDescription(
        key="load_optimized_start", pattern=TIME_PATTERN, icon="mdi:clock"
    ),
    TextEntityDescription(
        key="load_optimized_end", pattern=TIME_PATTERN, icon="mdi:clock"
    ),
    TextEntityDescription(
        key="load_period_1_start", pattern=TIME_PATTERN, icon="mdi:clock"
    ),
    TextEntityDescription(
        key="load_period_1_end", pattern=TIME_PATTERN, icon="mdi:clock"
    ),
    TextEntityDescription(
        key="load_period_2_start", pattern=TIME_PATTERN, icon="mdi:clock"
    ),
    TextEntityDescription(
        key="load_period_2_end", pattern=TIME_PATTERN, icon="mdi:clock"
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    coordinator: SungrowCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        KEY_COORDINATOR
    ]
    device_info: DeviceInfo = hass.data[DOMAIN][config_entry.entry_id][KEY_DEVICE_INFO]
    battery_info: DeviceInfo = hass.data[DOMAIN][config_entry.entry_id][
        KEY_BATTERY_INFO
    ]

    entities: list[Entity] = [
        SungrowText(
            coordinator,
            battery_info
            if description.key in BATTERY_DEVICE_VARIABLES
            else device_info,
            description,
        )
        for description in DESCRIPTIONS
        if description.key in coordinator.client.keys
    ]

    async_add_entities(entities)


class SungrowText(SungrowCoordinatorEntity, TextEntity):
    def __init__(
        self,
        coordinator: SungrowCoordinator,
        device_info: DeviceInfo,
        description: TextEntityDescription,
    ):
        super().__init__(coordinator, device_info, description)
        if self.variable.limits is not None:
            self._attr_native_min_value = self.variable.limits[0]
            self._attr_native_max_value = self.variable.limits[1]

    @property
    def native_value(self) -> Optional[str]:
        data = self.data
        if isinstance(data, time):
            return data.strftime("%H:%M")
        return self.data

    async def async_set_value(self, value: str) -> None:
        if self.variable.type == time:
            parsed = strptime(value, "%H:%M")
            value = time(hour=parsed.tm_hour, minute=parsed.tm_min)
        await self.set_data(value)
