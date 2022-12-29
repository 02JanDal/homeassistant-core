from typing import Any, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .const import (
    DOMAIN,
    KEY_COORDINATOR,
    KEY_DEVICE_INFO,
    KEY_BATTERY_INFO,
    BATTERY_DEVICE_VARIABLES,
)
from .coordinator import SungrowCoordinator, SungrowCoordinatorEntity

DESCRIPTIONS: tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription(
        key="battery_maintenance",
        entity_registry_enabled_default=False,
        icon="mdi:battery-sync",
    ),
    SwitchEntityDescription(
        key="export_power_limitation_enabled",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:transmission-tower-import",
    ),
    SwitchEntityDescription(
        key="off_grid_enabled",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        name="Off-grid enabled",
        icon="mdi:transmission-tower-off",
    ),
    SwitchEntityDescription(
        key="power_limitation",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        icon="mdi:car-speed-limiter",
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
        SungrowSwitch(
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


class SungrowSwitch(SungrowCoordinatorEntity, SwitchEntity):
    def __init__(
        self,
        coordinator: SungrowCoordinator,
        device_info: DeviceInfo,
        description: SwitchEntityDescription,
    ):
        super().__init__(coordinator, device_info, description)
        assert self.variable.type == bool

    @property
    def is_on(self) -> Optional[bool]:
        return self.data

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.set_data(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.set_data(False)
