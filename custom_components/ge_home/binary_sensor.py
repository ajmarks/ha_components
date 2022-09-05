"""GE Home Sensor Entities"""
import async_timeout
import logging
from typing import Callable

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN
from .devices import ApplianceApi
from .entities import GeErdBinarySensor
from .update_coordinator import GeHomeUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable):
    """GE Home binary sensors."""

    _LOGGER.debug('Adding GE Binary Sensor Entities')
    coordinator: GeHomeUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    #apis = coordinator.appliance_apis.values()

    @callback
    def async_devices_discovered(apis: list[ApplianceApi]):
        _LOGGER.debug(f'Found {len(apis):d} appliance APIs')

        entities = [
            entity
            for api in apis
            for entity in api.entities
            if isinstance(entity, GeErdBinarySensor) and not isinstance(entity, SwitchEntity)
        ]
        _LOGGER.debug(f'Found {len(entities):d} binary sensors')
        async_add_entities(entities)
    
    async_dispatcher_connect(hass, coordinator.signal_ready, async_devices_discovered)
