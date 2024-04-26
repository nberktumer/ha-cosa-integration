from coordinator import CosaCoordinator
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass, SensorStateClass, UnitOfTemperature
from homeassistant.const import PERCENTAGE
from homeassistant.core import callback

from .const import DOMAIN
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        name="Temperature",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        name="Humidity",
        state_class=SensorStateClass.MEASUREMENT,
    )
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        CosaSensorEntity(coordinator, idx, entity_description)
        for idx, ent in enumerate(coordinator.data)
        for entity_description in SENSOR_TYPES
    ]

    async_add_entities(entities)


class CosaSensorEntity(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: CosaCoordinator, idx: int, entity_description: SensorEntityDescription):
        super().__init__(coordinator)
        self.idx = idx
        self.entity_description = entity_description

        self.entity_id = "sensor.cosa_%s_%s" % (entity_description.key, coordinator.data[idx]["name"].lower())
        self._attr_unique_id = "sensor.cosa_%s_%s" % (entity_description.key, coordinator.data[idx]["id"])

        self._update_attrs(self.coordinator.data[self.idx])

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update_attrs(self.coordinator.data[self.idx])
        self.async_write_ha_state()

    @callback
    def _update_attrs(self, endpoint) -> None:
        self._attr_native_value = endpoint[self.entity_description.key]
