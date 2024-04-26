from coordinator import CosaCoordinator
from models.option import Option
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import callback

from const import DOMAIN, MIN_TEMPERATURE
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)

NUMBER_TYPES: tuple[SelectEntityDescription, ...] = (
    SelectEntityDescription(
        key="option",
        name="Combi State",
        options=list(map(str.capitalize, [Option.HOME, Option.SLEEP, Option.AWAY, Option.CUSTOM, Option.OFF])),
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        CosaSelectEntity(coordinator, idx, entity_description)
        for idx, ent in enumerate(coordinator.data)
        for entity_description in NUMBER_TYPES
    ]

    async_add_entities(entities)


class CosaSelectEntity(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator: CosaCoordinator, idx: int, entity_description: SelectEntityDescription):
        super().__init__(coordinator)
        self.idx = idx
        self.entity_description = entity_description

        self.entity_id = "select.cosa_%s_%s" % (entity_description.key, coordinator.data[idx]["name"].lower())
        self._attr_unique_id = "select.cosa_%s_%s" % (entity_description.key, coordinator.data[idx]["id"])

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

        if attr == Option.FROZEN:
            self._attr_current_option = Option.OFF.capitalize()
        else:
            self._attr_current_option = attr.capitalize()

    async def async_select_option(self, value: str) -> None:
        endpoint = self.coordinator.data[self.idx]
        value = value.lower()

        if value == Option.OFF:
            value = Option.FROZEN
            target_temp = MIN_TEMPERATURE
        elif value == Option.HOME:
            target_temp = endpoint["homeTemperature"]
        elif value == Option.SLEEP:
            target_temp = endpoint["sleepTemperature"]
        elif value == Option.AWAY:
            target_temp = endpoint["awayTemperature"]
        else:
            target_temp = endpoint["customTemperature"]

        self.coordinator.data[self.idx]["option"] = value
        self.coordinator.data[self.idx]["target_temperature"] = target_temp
        self.coordinator.async_set_updated_data(self.coordinator.data)
        await self.coordinator.cosa_api.set_option(endpoint["id"], Option(value))
        await self.coordinator.async_request_refresh()
