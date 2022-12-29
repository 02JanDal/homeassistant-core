from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.number import NumberEntityDescription, NumberEntity

from .const import (
    DOMAIN,
    KEY_COORDINATOR,
    KEY_DEVICE_INFO,
    KEY_BATTERY_INFO,
    BATTERY_DEVICE_VARIABLES,
)
from .coordinator import SungrowCoordinator, SungrowCoordinatorEntity

DESCRIPTIONS: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription(
        key="charge_discharge", name="Charge/Discharge", icon="mdi:battery-charging"
    ),
    NumberEntityDescription(
        key="export_power_limitation", icon="mdi:transmission-tower-import"
    ),
    NumberEntityDescription(
        key="load_optimized_power",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    NumberEntityDescription(
        key="min_soc",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        icon="mdi:battery-lock",
    ),
    NumberEntityDescription(
        key="max_soc",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        icon="mdi:battery-lock",
    ),
    NumberEntityDescription(
        key="power_limitation_adjustment",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        icon="mdi:car-speed-limiter",
    ),
    NumberEntityDescription(
        key="power_limitation_setting",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        icon="mdi:car-speed-limiter",
    ),
    NumberEntityDescription(
        key="reserved_soc_for_backup",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        icon="mdi:home-battery",
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
        SungrowNumber(
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


class SungrowNumber(SungrowCoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SungrowCoordinator,
        device_info: DeviceInfo,
        description: NumberEntityDescription,
    ):
        super().__init__(coordinator, device_info, description)
        assert self.variable.type in (int, float)

    @property
    def native_value(self) -> Optional[float]:
        return self.data

    async def async_set_native_value(self, value: float) -> None:
        if self.variable.type == int:
            value = int(value)
        await self.set_data(value)
