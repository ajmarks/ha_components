"""GE Kitchen Sensor Entities"""
import abc
import async_timeout
from datetime import timedelta
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from homeassistant.components.water_heater import (
    SUPPORT_OPERATION_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    WaterHeaterEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .entities import GeEntity, stringify_erd_value
from .const import DOMAIN

if TYPE_CHECKING:
    from .appliance_api import ApplianceApi
    from .update_coordinator import GeKitchenUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable):
    """GE Kitchen sensors."""
    _LOGGER.debug('Adding GE "Water Heaters"')
    coordinator: "GeKitchenUpdateCoordinator" = hass.data[DOMAIN][config_entry.entry_id]

    # This should be a NOP, but let's be safe
    with async_timeout.timeout(20):
        await coordinator.initialization_future
    _LOGGER.debug('Coordinator init future finished')

    apis = list(coordinator.appliance_apis.values())
    _LOGGER.debug(f'Found {len(apis):d} appliance APIs')
    entities = [
        entity for api in apis for entity in api.entities
        if isinstance(entity, WaterHeaterEntity)
    ]
    _LOGGER.debug(f'Found {len(entities):d} "water heaters"')
    async_add_entities(entities)
