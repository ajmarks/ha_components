"""Config flow for GE Kitchen integration."""

import asyncio
import logging
from typing import Dict, Optional

import aiohttp
import async_timeout
from gekitchen import GeAuthError, GeServerError, async_get_oauth2_token
import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import DOMAIN  # pylint:disable=unused-import
from .exceptions import AuthError, CannotConnect

_LOGGER = logging.getLogger(__name__)

GEKITCHEN_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect."""

    session = hass.helpers.aiohttp_client.async_get_clientsession(hass)

    # noinspection PyBroadException
    try:
        with async_timeout.timeout(10):
            _ = await async_get_oauth2_token(session, data[CONF_USERNAME], data[CONF_PASSWORD])
    except (asyncio.TimeoutError, aiohttp.ClientError):
        raise CannotConnect('Connection failure')
    except GeAuthError:
        raise AuthError('Authentication failure')
    except GeServerError:
        raise CannotConnect('Cannot connect (server error)')
    except Exception as exc:
        _LOGGER.exception("Unkown connection failure", exc_info=exc)
        raise CannotConnect('Unknown connection failure')

    # Return info that you want to store in the config entry.
    return {"title": f"GE Kitchen ({data[CONF_USERNAME]:s})"}


class GeKitchenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GE Kitchen."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_PUSH

    async def _async_validate_input(self, user_input):
        """Validate form input."""
        errors = {}
        info = None

        if user_input is not None:
            # noinspection PyBroadException
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except AuthError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        return info, errors

    async def async_step_user(self, user_input: Optional[Dict] = None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            info, errors = await self._async_validate_input(user_input)
            if info:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=GEKITCHEN_SCHEMA, errors=errors
        )

    async def async_step_reauth(self, user_input: Optional[dict] = None):
        """Handle re-auth if login is invalid."""
        errors = {}

        if user_input is not None:
            _, errors = await self._async_validate_input(user_input)

            if not errors:
                for entry in self._async_current_entries():
                    if entry.unique_id == self.unique_id:
                        self.hass.config_entries.async_update_entry(
                            entry, data=user_input
                        )
                        await self.hass.config_entries.async_reload(entry.entry_id)
                        return self.async_abort(reason="reauth_successful")

            if errors["base"] != "invalid_auth":
                return self.async_abort(reason=errors["base"])

        return self.async_show_form(
            step_id="reauth", data_schema=GEKITCHEN_SCHEMA, errors=errors,
        )
