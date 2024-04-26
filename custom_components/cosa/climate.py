from .coordinator import CosaCoordinator
from models.option import Option
from homeassistant.components.climate import ClimateEntity, HVACMode, ClimateEntityFeature, UnitOfTemperature
from homeassistant.const import PRECISION_TENTHS
from homeassistant.core import callback
import logging

from .const import DOMAIN, MIN_TEMPERATURE, MAX_TEMPERATURE
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [CosaClimateEntity(coordinator, idx) for idx, ent in enumerate(coordinator.data)], True
    )


class CosaClimateEntity(CoordinatorEntity, ClimateEntity):

    def __init__(self, coordinator: CosaCoordinator, idx: int):
        super().__init__(coordinator)
        self.idx = idx

        self.entity_id = "climate.cosa_%s" % coordinator.data[idx]["name"].lower()
        self._attr_unique_id = "climate.cosa_%s" % coordinator.data[idx]["id"]
        self._attr_target_temperature_step = PRECISION_TENTHS
        self._attr_precision = PRECISION_TENTHS
        self._attr_min_temp = MIN_TEMPERATURE
        self._attr_max_temp = MAX_TEMPERATURE
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_supported_features = (ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE)
        self._attr_preset_modes = list(
            map(str.capitalize, [Option.HOME, Option.AWAY, Option.SLEEP, Option.CUSTOM, Option.OFF]))
        self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]

        self._update_attr(self.coordinator.data[self.idx])

    async def async_set_temperature(self, **kwargs) -> None:
        temperature = kwargs.get("temperature")
        if temperature is None:
            return

        def pre_update_data(attr):
            self.coordinator.data[self.idx][attr] = temperature
            self.coordinator.async_set_updated_data(self.coordinator.data)

        endpoint = self.coordinator.data[self.idx]
        if endpoint["option"] == Option.HOME:
            pre_update_data("homeTemperature")
            await self.coordinator.cosa_api.set_target_temperatures(endpoint, home_temp=temperature)
        elif endpoint["option"] == Option.SLEEP:
            pre_update_data("sleepTemperature")
            await self.coordinator.cosa_api.set_target_temperatures(endpoint, sleep_temp=temperature)
        elif endpoint["option"] == Option.AWAY:
            pre_update_data("awayTemperature")
            await self.coordinator.cosa_api.set_target_temperatures(endpoint, away_temp=temperature)
        elif endpoint["option"] == Option.CUSTOM:
            pre_update_data("customTemperature")
            await self.coordinator.cosa_api.set_target_temperatures(endpoint, custom_temp=temperature)
        else:
            return

        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        endpoint = self.coordinator.data[self.idx]

        if hvac_mode == HVACMode.HEAT:
            option = endpoint["previousOption"]
        else:
            option = Option.OFF

        await self.async_set_preset_mode(option)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        endpoint = self.coordinator.data[self.idx]
        preset_mode = preset_mode.lower()
        if preset_mode == Option.OFF:
            preset_mode = Option.FROZEN
            target_temp = MIN_TEMPERATURE
        elif preset_mode == Option.HOME:
            target_temp = endpoint["homeTemperature"]
        elif preset_mode == Option.SLEEP:
            target_temp = endpoint["sleepTemperature"]
        elif preset_mode == Option.AWAY:
            target_temp = endpoint["awayTemperature"]
        else:
            target_temp = endpoint["customTemperature"]

        self.coordinator.data[self.idx]["option"] = preset_mode
        self.coordinator.data[self.idx]["target_temperature"] = target_temp
        self.coordinator.async_set_updated_data(self.coordinator.data)
        await self.coordinator.cosa_api.set_option(endpoint["id"], Option(preset_mode))
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update_attr(self.coordinator.data[self.idx])

        self.async_write_ha_state()

    @callback
    def _update_attr(self, endpoint):
        self._attr_name = endpoint["name"]
        self._attr_current_temperature = endpoint["temperature"]
        self._attr_target_temperature = endpoint["targetTemperature"]

        if endpoint["option"] == Option.FROZEN:
            self._attr_hvac_mode = HVACMode.OFF
            self._attr_preset_mode = Option.OFF.capitalize()
        else:
            self._attr_hvac_mode = HVACMode.HEAT
            self._attr_preset_mode = endpoint["option"].capitalize()
