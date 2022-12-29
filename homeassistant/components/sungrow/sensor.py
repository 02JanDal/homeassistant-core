from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional, Union

from collections.abc import Mapping

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pysungrow.definitions.device import SungrowDevice

from .const import (
    DOMAIN,
    KEY_COORDINATOR,
    KEY_DEVICE_INFO,
    KEY_BATTERY_INFO,
    BATTERY_DEVICE_VARIABLES,
)
from .coordinator import SungrowCoordinator, SungrowCoordinatorEntity

DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="protocol_number",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="protocol_version",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="arm_software_version",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="dsp_software_version",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="serial_number",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="device_type",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="nominal_output_power",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="output_type",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        device_class="sungrow__output_type",
    ),
    SensorEntityDescription(key="daily_output_energy"),
    SensorEntityDescription(key="total_output_energy"),
    SensorEntityDescription(
        key="total_running_time",
        device_class="duration",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="internal_temperature", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(
        key="mppt_1_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="mppt_2_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="dc_1_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="dc_2_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="dc_3_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="dc_4_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="mppt_1_current",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="mppt_2_current",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="dc_1_current",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="dc_2_current",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="dc_3_current",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="dc_4_current",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="total_dc_power",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:solar-panel-large",
    ),
    SensorEntityDescription(
        key="phase_a_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:transmission-tower",
    ),
    SensorEntityDescription(
        key="phase_b_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:transmission-tower",
    ),
    SensorEntityDescription(
        key="phase_c_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:transmission-tower",
    ),
    SensorEntityDescription(
        key="line_ab_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:transmission-tower",
    ),
    SensorEntityDescription(
        key="line_bc_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:transmission-tower",
    ),
    SensorEntityDescription(
        key="line_ca_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:transmission-tower",
    ),
    SensorEntityDescription(
        key="phase_a_current", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(
        key="phase_b_current", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(
        key="phase_c_current", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(
        key="total_active_power", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(
        key="reactive_power", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(
        key="power_factor",
        device_class="power_factor",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="grid_frequency",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:transmission-tower",
    ),
    # SensorEntityDescription(key="system_clock", entity_category=EntityCategory.CONFIG),
    SensorEntityDescription(key="daily_pv_generation", icon="mdi:solar-power-variant"),
    SensorEntityDescription(key="total_pv_generation", icon="mdi:solar-power-variant"),
    SensorEntityDescription(key="daily_export_from_pv", icon="mdi:solar-power-variant"),
    SensorEntityDescription(key="total_export_from_pv", icon="mdi:solar-power-variant"),
    SensorEntityDescription(
        key="load_power", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(
        key="export_power", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(
        key="daily_battery_charge_energy_from_pv", icon="mdi:solar-power-variant"
    ),
    SensorEntityDescription(
        key="total_battery_charge_energy_from_pv", icon="mdi:solar-power-variant"
    ),
    SensorEntityDescription(
        key="co2_reduction",
        entity_registry_enabled_default=False,
        icon="mdi:molecule-co2",
        name="CO₂ reduction",
    ),
    SensorEntityDescription(
        key="daily_direct_energy_consumption", icon="mdi:home-lightning-bolt"
    ),
    SensorEntityDescription(
        key="total_direct_energy_consumption", icon="mdi:home-lightning-bolt"
    ),
    SensorEntityDescription(
        key="battery_voltage", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(
        key="battery_current", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(
        key="battery_power", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(key="battery_level", device_class="battery"),
    SensorEntityDescription(
        key="battery_health",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:battery-heart",
    ),
    SensorEntityDescription(
        key="battery_temperature", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(key="daily_battery_discharge_energy"),
    SensorEntityDescription(key="total_battery_discharge_energy"),
    SensorEntityDescription(
        key="daily_self_consumption", icon="mdi:home-lightning-bolt"
    ),
    SensorEntityDescription(
        key="grid_state",
        icon="mdi:transmission-tower",
        device_class="sungrow__grid_state",
    ),
    SensorEntityDescription(
        key="daily_import_energy", icon="mdi:transmission-tower-export"
    ),
    SensorEntityDescription(
        key="total_import_energy", icon="mdi:transmission-tower-export"
    ),
    SensorEntityDescription(key="daily_charge_energy", icon="mdi:battery-charging"),
    SensorEntityDescription(key="total_charge_energy", icon="mdi:battery-charging"),
    SensorEntityDescription(
        key="drm_state",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="daily_export_energy", icon="mdi:transmission-tower-import"
    ),
    SensorEntityDescription(
        key="total_export_energy", icon="mdi:transmission-tower-import"
    ),
    SensorEntityDescription(key="battery_maintenance"),
    SensorEntityDescription(
        key="battery_type",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="battery_nominal_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="battery_capacity",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="battery_over_voltage_threshold",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="battery_under_voltage_threshold",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="battery_over_temperature_threshold",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        icon="mdi:temperature-alert",
    ),
    SensorEntityDescription(
        key="battery_under_temperature_threshold",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        icon="mdi:temperature-alert",
    ),
    SensorEntityDescription(
        key="grid_frequency_fine",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:transmission-tower",
    ),
    SensorEntityDescription(
        key="work_state", entity_category=EntityCategory.DIAGNOSTIC
    ),
    SensorEntityDescription(
        key="fault_date", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:alert"
    ),
    SensorEntityDescription(
        key="fault_code", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:alert"
    ),
    SensorEntityDescription(
        key="nominal_reactive_output_power",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="impedance_to_ground",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="daily_running_time",
        device_class="duration",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="country",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        icon="mdi:earth",
    ),
    SensorEntityDescription(
        key="monthly_power_yield", entity_registry_enabled_default=False
    ),
    SensorEntityDescription(
        key="negative_voltage_to_ground",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="bus_voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="power_factor_setting",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="reactive_power_adjustment",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="reactive_power_adjustment_switch",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="reactive_power_percentage",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
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
        SungrowSensor(
            coordinator,
            battery_info
            if description.key in BATTERY_DEVICE_VARIABLES
            else device_info,
            description,
        )
        for description in DESCRIPTIONS
        if description.key in coordinator.client.keys
    ]

    entities.append(SungrowStateSensor(coordinator, device_info))

    async_add_entities(entities)


class SungrowSensor(SungrowCoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator: SungrowCoordinator,
        device_info: DeviceInfo,
        description: SensorEntityDescription,
    ):
        super().__init__(coordinator, device_info, description)
        key = description.key

        # set entity metadata based on variable metadata
        variable = self.variable
        self._attr_native_unit_of_measurement = variable.unit
        if (
            key.startswith("total_")
            or key.startswith("daily_")
            or key.startswith("monthly_")
        ) and variable.unit == "kWh":
            self._attr_state_class = "total_increasing"
        elif variable.unit is not None:
            self._attr_state_class = "measurement"

        if (
            key.startswith("total_")
            and coordinator.client.variable(key.replace("total_", "daily_")) is not None
        ):
            # prefer daily sensors rather than total in the UI
            self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> Union[StateType, date, datetime, Decimal]:
        value = self.data
        if isinstance(value, Enum):
            return value.name.lower()
        elif isinstance(value, SungrowDevice):
            return value.name
        return value


class SungrowStateSensor(CoordinatorEntity[SungrowCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: SungrowCoordinator, device_info: DeviceInfo):
        super().__init__(coordinator)
        self._attr_device_info = device_info
        self._attr_unique_id = f"{DOMAIN}-{coordinator.serial_number}-state"
        self._attr_name = "State"
        self._attr_icon = "mdi:state-machine"
        self._attr_device_class = "sungrow__state"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_was_successful

    @property
    def native_value(self) -> Union[StateType, date, datetime, Decimal]:
        return self.coordinator.data["system_state"].name.lower()

    @property
    def extra_state_attributes(self) -> Optional[Mapping[str, Any]]:
        grid_state = self.coordinator.data["grid_state"]
        return {
            **self.coordinator.data["running_state"].to_dict(),
            grid_state: grid_state.name if grid_state else None,
        }
