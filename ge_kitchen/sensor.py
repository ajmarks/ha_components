"""GE Kitchen Sensor Entities"""
import async_timeout
import logging
from typing import Optional, Callable, TYPE_CHECKING

from gekitchen import ErdCodeType
from gekitchen.erd_constants import *

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .entities import (
    TEMPERATURE_ERD_CODES,
    GeErdEntity,
    get_erd_icon,
    get_erd_units,
    stringify_erd_value,
)

if TYPE_CHECKING:
    from .update_coordinator import GeKitchenUpdateCoordinator
    from .appliance_api import ApplianceApi


_LOGGER = logging.getLogger(__name__)


class GeErdSensor(GeErdEntity, Entity):
    """GE Entity for sensors"""
    @property
    def state(self) -> Optional[str]:
        try:
            value = self.appliance.get_erd_value(self.erd_code)
        except KeyError:
            return None
        return stringify_erd_value(self.erd_code, value, self.units)

    @property
    def measurement_system(self) -> Optional[ErdMeasurementUnits]:
        return self.appliance.get_erd_value(ErdCode.TEMPERATURE_UNIT)

    @property
    def units(self) -> Optional[str]:
        return get_erd_units(self.erd_code, self.measurement_system)

    @property
    def device_class(self) -> Optional[str]:
        if self.erd_code in TEMPERATURE_ERD_CODES:
            return DEVICE_CLASS_TEMPERATURE
        return None

    @property
    def icon(self) -> Optional[str]:
        return get_erd_icon(self.erd_code, self.state)

    @property
    def unit_of_measurement(self) -> Optional[str]:
        if self.device_class == DEVICE_CLASS_TEMPERATURE:
            return self.units


class GeErdPropertySensor(GeErdSensor):
    """GE Entity for sensors"""
    def __init__(self, api: "ApplianceApi", erd_code: ErdCodeType, erd_property: str):
        super().__init__(api, erd_code)
        self.erd_property = erd_property

    @property
    def unique_id(self) -> Optional[str]:
        return f"{super().unique_id}_{self.erd_property}"

    @property
    def name(self) -> Optional[str]:
        base_string = super().name
        property_name = self.erd_property.replace("_", " ").title()
        return f"{base_string} {property_name}"

    @property
    def state(self) -> Optional[str]:
        try:
            value = getattr(self.appliance.get_erd_value(self.erd_code), self.erd_property)
        except KeyError:
            return None
        return stringify_erd_value(self.erd_code, value, self.units)

    @property
    def measurement_system(self) -> Optional[ErdMeasurementUnits]:
        return self.appliance.get_erd_value(ErdCode.TEMPERATURE_UNIT)

    @property
    def units(self) -> Optional[str]:
        return get_erd_units(self.erd_code, self.measurement_system)

    @property
    def device_class(self) -> Optional[str]:
        if self.erd_code in TEMPERATURE_ERD_CODES:
            return "temperature"
        return None


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable):
    """GE Kitchen sensors."""
    _LOGGER.debug('Adding GE Kitchen sensors')
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
        if isinstance(entity, GeErdSensor) and entity.erd_code in api.appliance._property_cache
    ]
    _LOGGER.debug(f'Found {len(entities):d} sensors')
    async_add_entities(entities)
