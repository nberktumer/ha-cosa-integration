from typing import TypeVar, Optional

from models.auth import AuthRequest
from models.base import BaseRequest
from models.combi import SetCombiSettingsRequest
from models.device import SetDeviceSettingsRequest
from models.endpoint import GetEndpointRequest, \
    GetEndpointClientsRequest
from models.mode import Mode, SetModeRequest
from models.option import Option, SetOptionRequest
from models.place import GetPlaceRequest
from models.settings import CombiSettings
from models.temperature import TargetTemperatures, GetTargetTemperaturesRequest, \
    SetTargetTemperaturesRequest
from .exceptions import ApiAuthError, InvalidAuth, CannotConnect, ApiError

from aiohttp import ClientSession

T = TypeVar('T')


class CosaApi:
    HOST = "https://kiwi.cosa.com.tr"

    def __init__(self, session: ClientSession, auth_token: Optional[str] = None, verbose: bool = False) -> None:
        self.session = session
        self.auth_token = auth_token
        self.verbose = verbose

    async def authenticate(self, email: str, password: str) -> str:
        dto = AuthRequest(email=email, password=password)
        result = await self._cosa_request("api/users/login", dto=dto, auth=False)

        self.auth_token = result["authToken"]
        return result["authToken"]

    async def get_user(self):
        result = await self._cosa_request("api/users/getInfo")
        return result["user"]

    async def get_endpoints(self):
        result = await self._cosa_request("api/endpoints/getEndpoints")
        return result["endpoints"]

    async def get_endpoint_info(self, endpoint_id: str):
        dto = GetEndpointRequest(endpoint=endpoint_id)
        result = await self._cosa_request("api/endpoints/getEndpoint", dto=dto)
        return result["endpoint"]

    async def get_endpoint_clients(self, endpoint_id: str):
        dto = GetEndpointClientsRequest(endpoint=endpoint_id)
        result = await self._cosa_request("api/endpointClients/getEndpointClients", dto=dto)
        return result["endpointClients"]

    async def get_place(self, place_id: str):
        dto = GetPlaceRequest(place=place_id)
        result = await self._cosa_request("api/places/getPlace", dto=dto)
        return result["place"]

    async def get_target_temperatures(self, endpoint_id: str):
        dto = GetTargetTemperaturesRequest(endpoint=endpoint_id)
        result = await self._cosa_request("api/endpoints/getTargetTemperatures", dto=dto)
        return result["targetTemperatures"]

    async def set_target_temperatures(self, endpoint, away_temp: Optional[float] = None,
                                      custom_temp: Optional[float] = None, home_temp: Optional[float] = None,
                                      sleep_temp: Optional[float] = None) -> bool:
        if away_temp is None:
            away_temp = endpoint["awayTemperature"]
        if custom_temp is None:
            custom_temp = endpoint["customTemperature"]
        if home_temp is None:
            home_temp = endpoint["homeTemperature"]
        if sleep_temp is None:
            sleep_temp = endpoint["sleepTemperature"]

        dto = SetTargetTemperaturesRequest(
            endpoint=endpoint["id"],
            targetTemperatures=TargetTemperatures(
                away=away_temp,
                custom=custom_temp,
                home=home_temp,
                sleep=sleep_temp
            )
        )
        result = await self._cosa_request("api/endpoints/setTargetTemperatures", dto=dto)
        return result.get("ok") == 1

    async def set_option(self, endpoint_id: str, option: Option) -> bool:
        dto = SetOptionRequest(endpoint=endpoint_id, option=option)
        result = await self._cosa_request("api/endpoints/setOption", dto=dto)
        return result.get("ok") == 1

    async def set_mode(self, endpoint_id: str, mode: Mode, option: Option) -> bool:
        dto = SetModeRequest(endpoint=endpoint_id, mode=mode, option=option)
        result = await self._cosa_request("api/endpoints/setMode", dto=dto)
        return result.get("ok") == 1

    async def set_combi_settings(self, endpoint, pid_window_low: Optional[float] = None,
                                 pid_window_high: Optional[float] = None) -> bool:
        if pid_window_low is None:
            pid_window_low = endpoint["combiSettings"]["pidWindowLow"]
        if pid_window_high is None:
            pid_window_high = endpoint["combiSettings"]["pidWindowHigh"]

        dto = SetCombiSettingsRequest(
            endpoint=endpoint["id"],
            combiSettings=CombiSettings(
                heating=True,
                pidWindowLow=pid_window_low,
                pidWindowHigh=pid_window_high
            )
        )
        result = await self._cosa_request("api/endpoints/setCombiSettings", dto=dto)
        return result.get("ok") == 1

    async def set_device_settings(self, endpoint_id: str, calibration: float) -> bool:
        dto = SetDeviceSettingsRequest(endpoint=endpoint_id, calibration=calibration)
        result = await self._cosa_request("api/endpoints/setDeviceSettings", dto=dto)
        return result.get("ok") == 1

    async def _cosa_request(self, path: str, dto: BaseRequest = BaseRequest(), auth=True):
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=utf-8"
        }
        if auth:
            headers["authToken"] = self.auth_token

        async with self.session.post("%s/%s" % (self.HOST, path), headers=headers, json=dto.dict()) as response:
            if not response or response.status < 200 or response.status >= 400:
                raise CannotConnect

            result = await response.json()
            if self.verbose:
                print(result)

            if not result or not result.get("ok"):
                if result.get("code") == 111:
                    raise InvalidAuth
                if result.get("code") == 104:
                    raise ApiAuthError
                error = result.get("error")
                if error:
                    raise ApiError(error[0]["message"])
                raise ApiError("Something went wrong")

            return result
