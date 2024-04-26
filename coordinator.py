import asyncio
import logging
from datetime import timedelta

from .const import DOMAIN
from .api import CosaApi
from .exceptions import ApiAuthError, ApiError
from .models.mode import Mode
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import async_timeout

_LOGGER = logging.getLogger(__name__)


class CosaCoordinator(DataUpdateCoordinator):
    UPDATE_DATA_INTERVAL = timedelta(seconds=10)
    UPDATE_ENDPOINTS_INTERVAL = timedelta(hours=1)

    def __init__(self, hass: HomeAssistant, cosa_api: CosaApi):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=self.UPDATE_DATA_INTERVAL,
        )

        self._update_endpoint_counter = 0
        self._endpoints = []
        self.cosa_api = cosa_api

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(15):
                self._update_endpoint_counter -= 1
                if self._update_endpoint_counter <= 0:
                    self._update_endpoint_counter = round(self.UPDATE_DATA_INTERVAL / self.UPDATE_ENDPOINTS_INTERVAL)
                    self._endpoints = await self.cosa_api.get_endpoints()

                result = await asyncio.gather(*[self.cosa_api.get_endpoint_info(x["id"]) for x in self._endpoints])
                tasks = []
                for endpoint in result:
                    if endpoint["mode"] != Mode.MANUAL:
                        tasks.append(self.cosa_api.set_mode(endpoint["id"], Mode.MANUAL, endpoint["option"]))
                await asyncio.gather(*tasks)

                return result
        except ApiAuthError as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
