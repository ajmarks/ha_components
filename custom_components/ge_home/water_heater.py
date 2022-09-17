"""GE Home Sensor Entities"""
import async_timeout
import logging
from typing import Callable

from homeassistant.components.water_heater import WaterHeaterEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers import entity_registry as er

from .entities import GeAbstractWaterHeater
from .const import DOMAIN
from .devices import ApplianceApi
from .update_coordinator import GeHomeUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable):
    """GE Home Water Heaters."""
    _LOGGER.debug('Adding GE "Water Heaters"')
    coordinator: GeHomeUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    registry = er.async_get(hass)

    @callback
    def async_devices_discovered(apis: list[ApplianceApi]):
        _LOGGER.debug(f'Found {len(apis):d} appliance APIs')
        entities = [
            entity 
            for api in apis 
            for entity in api.entities
            if isinstance(entity, GeAbstractWaterHeater)
            if not registry.async_is_registered(entity.entity_id)
        ]
        _LOGGER.debug(f'Found {len(entities):d} unregistered water heaters')
        async_add_entities(entities)

    async_dispatcher_connect(hass, coordinator.signal_ready, async_devices_discovered)
