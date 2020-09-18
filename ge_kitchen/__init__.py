"""The ge_kitchen integration."""

import asyncio
import async_timeout
import logging
import voluptuous as vol

from gekitchen import GeAuthError, GeServerError

from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.const import CONF_USERNAME
from homeassistant.core import HomeAssistant
from . import config_flow
from .const import (
    AUTH_HANDLER,
    COORDINATOR,
    DOMAIN,
    OAUTH2_AUTH_URL,
    OAUTH2_TOKEN_URL,
)
from .exceptions import AuthError, CannotConnect
from .update_coordinator import GeKitchenUpdateCoordinator

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)
PLATFORMS = ["binary_sensor", "sensor", "switch", "water_heater"]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the ge_kitchen component."""
    hass.data.setdefault(DOMAIN, {})
    if DOMAIN not in config:
        return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up ge_kitchen from a config entry."""
    coordinator = GeKitchenUpdateCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = coordinator

    try:
        await coordinator.async_start_client()
    except GeAuthError:
        raise AuthError('Authentication failure')
    except GeServerError:
        raise CannotConnect('Cannot connect (server error)')
    except Exception:
        raise CannotConnect('Unknown connection failure')

    try:
        with async_timeout.timeout(30):
            await coordinator.initialization_future
    except TimeoutError:
        raise CannotConnect('Initialization timed out')

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_update_options(hass, config_entry):
    """Update options."""
    await hass.config_entries.async_reload(config_entry.entry_id)
