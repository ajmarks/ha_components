"""Exceptions go here."""

from homeassistant import exceptions as ha_exc


class CannotConnect(ha_exc.HomeAssistantError):
    """Error to indicate we cannot connect."""


class AuthError(ha_exc.HomeAssistantError):
    """Error to indicate authentication failure."""
