"""GE Kitchen Sensor Entities"""
import async_timeout
import logging
from typing import Callable, TYPE_CHECKING

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .binary_sensor import GeErdBinarySensor
from .const import DOMAIN

if TYPE_CHECKING:
    from .update_coordinator import GeKitchenUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class GeErdSwitch(GeErdBinarySensor, SwitchEntity):
    """Switches for boolean ERD codes."""
    device_class = "switch"

    @property
    def is_on(self) -> bool:
        """Return True if switch is on."""
        return bool(self.appliance.get_erd_value(self.erd_code))

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.debug(f"Turning on {self.unique_id}")
        await self.appliance.async_set_erd_value(self.erd_code, True)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        _LOGGER.debug(f"Turning on {self.unique_id}")
        await self.appliance.async_set_erd_value(self.erd_code, False)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable):
    """GE Kitchen sensors."""
    _LOGGER.debug('Adding GE Kitchen switches')
    coordinator: "GeKitchenUpdateCoordinator" = hass.data[DOMAIN][config_entry.entry_id]

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
        if isinstance(entity, GeErdSwitch) and entity.erd_code in api.appliance._property_cache
    ]
    _LOGGER.debug(f'Found {len(entities):d} switches')
    async_add_entities(entities)
