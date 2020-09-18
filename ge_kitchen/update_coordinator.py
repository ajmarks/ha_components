"""Data update coordinator for shark iq vacuums."""

import asyncio
import logging
from typing import Any, Dict, Iterable, Optional, Tuple

from gekitchen import (
    EVENT_APPLIANCE_INITIAL_UPDATE,
    EVENT_APPLIANCE_UPDATE_RECEIVED,
    EVENT_CONNECTED,
    EVENT_DISCONNECTED,
    EVENT_GOT_APPLIANCE_LIST,
    ErdCodeType,
    GeAppliance,
    GeWebsocketClient,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, EVENT_ALL_APPLIANCES_READY, UPDATE_INTERVAL
from .appliance_api import ApplianceApi, get_appliance_api_type

_LOGGER = logging.getLogger(__name__)


class GeKitchenUpdateCoordinator(DataUpdateCoordinator):
    """Define a wrapper class to update Shark IQ data."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Set up the SharkIqUpdateCoordinator class."""
        self._hass = hass
        self._config_entry = config_entry
        self._username = config_entry.data[CONF_USERNAME]
        self._password = config_entry.data[CONF_PASSWORD]
        self.client = None  # type: Optional[GeWebsocketClient]
        self._appliance_apis = {}  # type: Dict[str, ApplianceApi]

        # Some record keeping to let us know when we can start generating entities
        self._got_roster = False
        self._init_done = False
        self.initialization_future = asyncio.Future()

        super().__init__(hass, _LOGGER, name=DOMAIN)

    def create_ge_client(self, event_loop: Optional[asyncio.AbstractEventLoop]) -> GeWebsocketClient:
        """
        Create a new GeClient object with some helpful callbacks.

        :param event_loop: Event loop
        :return: GeWebsocketClient
        """
        client = GeWebsocketClient(event_loop=event_loop, username=self._username, password=self._password)
        client.add_event_handler(EVENT_APPLIANCE_INITIAL_UPDATE, self.on_device_initial_update)
        client.add_event_handler(EVENT_APPLIANCE_UPDATE_RECEIVED, self.on_device_update)
        client.add_event_handler(EVENT_GOT_APPLIANCE_LIST, self.on_appliance_list)
        client.add_event_handler(EVENT_DISCONNECTED, self.on_disconnect)
        client.add_event_handler(EVENT_CONNECTED, self.on_connect)
        return client

    @property
    def appliances(self) -> Iterable[GeAppliance]:
        return self.client.appliances.values()

    @property
    def appliance_apis(self) -> Dict[str, ApplianceApi]:
        return self._appliance_apis

    def _get_appliance_api(self, appliance: GeAppliance) -> ApplianceApi:
        api_type = get_appliance_api_type(appliance.appliance_type)
        return api_type(self, appliance)

    def regenerate_appliance_apis(self):
        """Regenerate the appliance_apis dictionary, adding elements as necessary."""
        for jid, appliance in self.client.appliances.keys():
            if jid not in self._appliance_apis:
                self._appliance_apis[jid] = self._get_appliance_api(appliance)

    def maybe_add_appliance_api(self, appliance: GeAppliance):
        mac_addr = appliance.mac_addr
        if mac_addr not in self.appliance_apis:
            _LOGGER.debug(f"Adding appliance api for appliance {mac_addr} ({appliance.appliance_type})")
            api = self._get_appliance_api(appliance)
            api.build_entities_list()
            self.appliance_apis[mac_addr] = api

    async def get_client(self) -> GeWebsocketClient:
        """Get a new GE Websocket client."""
        if self.client is not None:
            await self.client.disconnect()

        loop = self._hass.loop
        self.client = self.create_ge_client(event_loop=loop)
        return self.client

    async def async_start_client(self):
        """Start a new GeClient in the HASS event loop."""
        _LOGGER.debug('Running client')
        client = await self.get_client()

        session = self._hass.helpers.aiohttp_client.async_get_clientsession()
        await client.async_get_credentials(session)
        fut = asyncio.ensure_future(client.async_run_client(), loop=self._hass.loop)
        _LOGGER.debug('Client running')
        return fut

    async def _kill_client(self):
        """Kill the client.  Leaving this in for testing purposes."""
        await asyncio.sleep(30)
        _LOGGER.critical('Killing the connection.  Popcorn time.')
        await self.client.websocket.close()

    async def on_device_update(self, data: Tuple[GeAppliance, Dict[ErdCodeType, Any]]):
        """Let HA know there's new state."""
        self.last_update_success = True
        appliance, _ = data
        try:
            api = self.appliance_apis[appliance.mac_addr]
        except KeyError:
            return
        for entity in api.entities:
            _LOGGER.debug(f'Updating {entity} ({entity.unique_id}, {entity.entity_id})')
            entity.async_write_ha_state()

    @property
    def all_appliances_updated(self) -> bool:
        """True if all appliances have had an initial update."""
        return all([a.initialized for a in self.appliances])

    async def on_appliance_list(self, _):
        """When we get an appliance list, mark it and maybe trigger all ready."""
        _LOGGER.debug('Got roster update')
        self.last_update_success = True
        if not self._got_roster:
            self._got_roster = True
            await asyncio.sleep(5)  # After the initial roster update, wait a bit and hit go
            await self.async_maybe_trigger_all_ready()

    async def on_device_initial_update(self, appliance: GeAppliance):
        """When an appliance first becomes ready, let the system know and schedule periodic updates."""
        _LOGGER.debug(f'Got initial update for {appliance.mac_addr}')
        self.last_update_success = True
        self.maybe_add_appliance_api(appliance)
        await self.async_maybe_trigger_all_ready()
        _LOGGER.debug(f'Requesting updates for {appliance.mac_addr}')
        while not self.client.websocket.closed and appliance.available:
            await asyncio.sleep(UPDATE_INTERVAL)
            await appliance.async_request_update()
        _LOGGER.debug(f'No longer requesting updates for {appliance.mac_addr}')

    async def on_disconnect(self, _):
        """Handle disconnection."""
        _LOGGER.debug("Disconnected. Attempting to reconnect.")
        self.last_update_success = False

        flow_context = {
            "source": "reauth",
            "unique_id": self._config_entry.unique_id,
        }

        matching_flows = [
            flow
            for flow in self.hass.config_entries.flow.async_progress()
            if flow["context"] == flow_context
        ]

        if not matching_flows:
            self.hass.async_create_task(
                self.hass.config_entries.flow.async_init(
                    DOMAIN, context=flow_context, data=self._config_entry.data,
                )
            )

    async def on_connect(self, _):
        """Set state upon connection."""
        self.last_update_success = True

    async def async_maybe_trigger_all_ready(self):
        """See if we're all ready to go, and if so, let the games begin."""
        if self._init_done or self.initialization_future.done():
            # Been here, done this
            return
        if self._got_roster and self.all_appliances_updated:
            _LOGGER.debug('Ready to go.  Waiting 2 seconds and setting init future result.')
            # The the flag and wait to prevent two different fun race conditions
            self._init_done = True
            await asyncio.sleep(2)
            self.initialization_future.set_result(True)
            await self.client.async_event(EVENT_ALL_APPLIANCES_READY, None)
