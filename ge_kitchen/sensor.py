"""GE Kitchen Sensor Entities"""
import async_timeout
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from typing import Callable
from .update_coordinator import GeKitchenUpdateCoordinator
from .appliance_api import GeSensor
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable):
    """GE Kitchen sensors."""
    _LOGGER.debug('Adding GE Kitchen sensors')
    coordinator = hass.data[DOMAIN][config_entry.entry_id]  # type: GeKitchenUpdateCoordinator

    # This should be a NOP, but let's be safe
    with async_timeout.timeout(20):
        await coordinator.initialization_future
    _LOGGER.debug('Coordinator init future finished')

    apis = list(coordinator.appliance_apis.values())
    _LOGGER.debug(f'Found {len(apis):d} appliance APIs')
    entities = [
        entity
        for api in apis
        for entity in api.entities
        if isinstance(entity, GeSensor) and entity.erd_code in api.appliance._property_cache
    ]
    _LOGGER.debug(f'Found {len(entities):d} sensors')
    async_add_entities(entities)
