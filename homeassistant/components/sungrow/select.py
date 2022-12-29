from enum import Enum
from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.select import SelectEntityDescription, SelectEntity
from pysungrow.definitions.variables.general import StartStop
from pysungrow.definitions.variables.hybrid import (
    ChargeDischargeCommand,
    EMSMode,
    LoadAdjustmentMode,
    OnOffMode,
)

from .const import (
    DOMAIN,
    KEY_COORDINATOR,
    KEY_DEVICE_INFO,
    KEY_BATTERY_INFO,
    BATTERY_DEVICE_VARIABLES,
)
from .coordinator import SungrowCoordinator, SungrowCoordinatorEntity


def make_options(enum: type[Enum]):
    return [opt.name.lower() for opt in enum]


DESCRIPTIONS: tuple[SelectEntityDescription, ...] = (
    SelectEntityDescription(
        key="charge_discharge_command",
        options=make_options(ChargeDischargeCommand),
        name="Charge/Discharge Command",
        icon="mdi:battery-charging",
    ),
    SelectEntityDescription(
        key="ems_mode",
        options=make_options(EMSMode),
        entity_category=EntityCategory.CONFIG,
        name="EMS mode",
        icon="mdi:cog",
    ),
    SelectEntityDescription(
        key="load_adjustment_mode", options=make_options(LoadAdjustmentMode)
    ),
    SelectEntityDescription(
        key="load_on_off_mode", options=make_options(OnOffMode), name="Load On/Off Mode"
    ),
    SelectEntityDescription(
        key="start_stop",
        options=make_options(StartStop),
        icon="mdi:power-standby",
        name="Start/Stop",
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
        SungrowSelect(
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


class SungrowSelect(SungrowCoordinatorEntity, SelectEntity):
    def __init__(
        self,
        coordinator: SungrowCoordinator,
        device_info: DeviceInfo,
        description: SelectEntityDescription,
    ):
        super().__init__(coordinator, device_info, description)
        assert issubclass(self.variable.type, Enum)

    @property
    def device_class(self) -> Optional[str]:
        return f"sungrow__{self.entity_description.key}"

    @property
    def current_option(self) -> Optional[str]:
        return self.data.name.lower() if self.data else None

    async def async_select_option(self, option: str) -> None:
        enum = self.variable.type
        value = next(opt for opt in enum if opt.name.lower() == option)
        await self.set_data(value)
