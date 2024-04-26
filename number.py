from dataclasses import dataclass
from typing import Callable, Any

from .coordinator import CosaCoordinator
from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberDeviceClass, UnitOfTemperature
from homeassistant.const import PRECISION_TENTHS
from homeassistant.core import callback

from .const import DOMAIN
from .api import CosaApi
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)


@dataclass
class CosaNumberEntityDescription(NumberEntityDescription):
    set_value_func: Callable = None


async def set_combi_settings(api: CosaApi, endpoint, key: str, value: Any):
    kwargs = {key: value}
    await api.set_combi_settings(endpoint, **kwargs)


async def set_device_settings(api: CosaApi, endpoint, key: str, value: Any):
    kwargs = {key: value}
    await api.set_device_settings(endpoint["id"], **kwargs)


NUMBER_TYPES: tuple[CosaNumberEntityDescription, ...] = (
    CosaNumberEntityDescription(
        key="pidWindowLow",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        name="PID Start Window",
        native_step=PRECISION_TENTHS,
        native_min_value=0.0,
        native_max_value=0.5,
        set_value_func=set_combi_settings,
        icon="mdi:thermometer-chevron-down"
    ),
    CosaNumberEntityDescription(
        key="pidWindowHigh",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        name="PID End Window",
        native_step=PRECISION_TENTHS,
        native_min_value=0.1,
        native_max_value=0.5,
        set_value_func=set_combi_settings,
        icon="mdi:thermometer-chevron-up"
    ),
    CosaNumberEntityDescription(
        key="calibration",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        name="Temperature Calibration",
        native_step=PRECISION_TENTHS,
        native_min_value=-1.0,
        native_max_value=1.0,
        set_value_func=set_device_settings,
        icon="mdi:thermometer"
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Config entry example."""
    # assuming API object stored here by __init__.py
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        CosaNumberEntity(coordinator, idx, entity_description)
        for idx, ent in enumerate(coordinator.data)
        for entity_description in NUMBER_TYPES
    ]

    async_add_entities(entities)


class CosaNumberEntity(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator: CosaCoordinator, idx: int, entity_description: CosaNumberEntityDescription):
        super().__init__(coordinator)
        self.idx = idx
        self.entity_description: CosaNumberEntityDescription = entity_description

        self.entity_id = "number.cosa_%s_%s" % (entity_description.key, coordinator.data[idx]["name"].lower())
        self._attr_unique_id = "number.cosa_%s_%s" % (entity_description.key, coordinator.data[idx]["id"])

        self._update_attrs(self.coordinator.data[self.idx])

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update_attrs(self.coordinator.data[self.idx])
        self.async_write_ha_state()

    @callback
    def _update_attrs(self, endpoint) -> None:
        keys = self.entity_description.key.split("|")
        attr = endpoint
        for key in keys:
            attr = attr[key]

        self._attr_native_value = attr

    async def async_set_native_value(self, value: float) -> None:
        setattr(self.coordinator.data[self.idx], self.entity_description.key, value)
        self.coordinator.async_set_updated_data(self.coordinator.data)

        await self.entity_description.set_value_func(self.coordinator.cosa_api, self.coordinator.data[self.idx],
                                                     self.entity_description.key, value)
        await self.coordinator.async_request_refresh()
