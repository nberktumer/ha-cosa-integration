from dataclasses import dataclass
from typing import Any

from .coordinator import CosaCoordinator
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription, \
    BinarySensorDeviceClass
from homeassistant.core import callback

from .const import DOMAIN
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)
from models.option import Option


@dataclass
class CosaBinarySensorEntityDescription(BinarySensorEntityDescription):
    condition: Any = True


BINARY_SENSOR_TYPES: tuple[CosaBinarySensorEntityDescription, ...] = (
    CosaBinarySensorEntityDescription(
        key="combiState",
        device_class=BinarySensorDeviceClass.POWER,
        name="Heater Status",
        condition="on",
        icon="mdi:thermometer"
    ),
    CosaBinarySensorEntityDescription(
        key="option",
        device_class=BinarySensorDeviceClass.POWER,
        name="Is Preset Home Selected",
        condition=Option.HOME,
    ),
    CosaBinarySensorEntityDescription(
        key="option",
        device_class=BinarySensorDeviceClass.POWER,
        name="Is Away Preset Selected",
        condition=Option.AWAY,
    ),
    CosaBinarySensorEntityDescription(
        key="option",
        device_class=BinarySensorDeviceClass.POWER,
        name="Is Sleep Preset Selected",
        condition=Option.SLEEP,
    ),
    CosaBinarySensorEntityDescription(
        key="option",
        device_class=BinarySensorDeviceClass.POWER,
        name="Is Custom Preset Selected",
        condition=Option.CUSTOM,
    ),
    CosaBinarySensorEntityDescription(
        key="option",
        device_class=BinarySensorDeviceClass.POWER,
        name="Is Off Preset Selected",
        condition=Option.FROZEN,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Config entry example."""
    # assuming API object stored here by __init__.py
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        CosaBinarySensorEntity(coordinator, idx, entity_description, entity_id)
        for idx, ent in enumerate(coordinator.data)
        for entity_id, entity_description in enumerate(BINARY_SENSOR_TYPES)
    ]

    async_add_entities(entities)


class CosaBinarySensorEntity(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator: CosaCoordinator, idx: int, entity_description: CosaBinarySensorEntityDescription,
                 entity_id: int):
        super().__init__(coordinator)
        self.idx = idx
        self.entity_description: CosaBinarySensorEntityDescription = entity_description

        self.entity_id = "binary_sensor.cosa_%s_%s_%s" % (
            entity_description.key, coordinator.data[idx]["name"].lower(), entity_id)
        self._attr_unique_id = "binary_sensor.cosa_%s_%s_%s" % (
            entity_description.key, coordinator.data[idx]["id"], entity_id)

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

        self._attr_is_on = attr == self.entity_description.condition
