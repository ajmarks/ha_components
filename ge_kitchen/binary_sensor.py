"""GE Kitchen Sensor Entities"""
import async_timeout
import logging
from typing import Callable, Optional, TYPE_CHECKING

from gekitchen import ErdCodeType

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .entities import DOOR_ERD_CODES, GeErdEntity, boolify_erd_value, get_erd_icon

if TYPE_CHECKING:
    from .appliance_api import ApplianceApi
    from .update_coordinator import GeKitchenUpdateCoordinator


_LOGGER = logging.getLogger(__name__)


class GeErdBinarySensor(GeErdEntity, BinarySensorEntity):
    """GE Entity for binary sensors"""
    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return bool(self.appliance.get_erd_value(self.erd_code))

    @property
    def icon(self) -> Optional[str]:
        return get_erd_icon(self.erd_code, self.is_on)

    @property
    def device_class(self) -> Optional[str]:
        if self.erd_code in DOOR_ERD_CODES:
            return "door"
        return None


class GeErdPropertyBinarySensor(GeErdBinarySensor):
    """GE Entity for property binary sensors"""
    def __init__(self, api: "ApplianceApi", erd_code: ErdCodeType, erd_property: str):
        super().__init__(api, erd_code)
        self.erd_property = erd_property

    @property
    def is_on(self) -> Optional[bool]:
        """Return True if entity is on."""
        try:
            value = getattr(self.appliance.get_erd_value(self.erd_code), self.erd_property)
        except KeyError:
            return None
        return boolify_erd_value(self.erd_code, value)

    @property
    def icon(self) -> Optional[str]:
        return get_erd_icon(self.erd_code, self.is_on)

    @property
    def unique_id(self) -> Optional[str]:
        return f"{super().unique_id}_{self.erd_property}"

    @property
    def name(self) -> Optional[str]:
        base_string = super().name
        property_name = self.erd_property.replace("_", " ").title()
        return f"{base_string} {property_name}"


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable):
    """GE Kitchen sensors."""

    coordinator: "GeKitchenUpdateCoordinator" = hass.data[DOMAIN][config_entry.entry_id]

    # This should be a NOP, but let's be safe
    with async_timeout.timeout(20):
        await coordinator.initialization_future

    apis = coordinator.appliance_apis.values()
    _LOGGER.debug(f'Found {len(apis):d} appliance APIs')
    entities = [
        entity
        for api in apis
        for entity in api.entities
        if isinstance(entity, GeErdBinarySensor) and not isinstance(entity, SwitchEntity)
    ]
    _LOGGER.debug(f'Found {len(entities):d} binary sensors  ')
    async_add_entities(entities)
