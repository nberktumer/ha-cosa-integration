from homeassistant.exceptions import HomeAssistantError


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class ApiAuthError(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class ApiError(HomeAssistantError):
    """Error to indicate there is invalid auth."""
