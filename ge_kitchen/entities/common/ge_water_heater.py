import abc
from typing import Any, Dict, List, Optional

from homeassistant.components.water_heater import WaterHeaterEntity
from homeassistant.const import (
    TEMP_FAHRENHEIT,
    TEMP_CELSIUS
)
from gekitchen import ErdCode, ErdMeasurementUnits
from ge_kitchen.const import DOMAIN
from .ge_erd_entity import GeEntity

class GeWaterHeater(GeEntity, WaterHeaterEntity, metaclass=abc.ABCMeta):
    """Mock temperature/operation mode supporting device as a water heater"""

    @property
    def heater_type(self) -> str:
        raise NotImplementedError

    @property
    def operation_list(self) -> List[str]:
        raise NotImplementedError

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}_{self.serial_number}_{self.heater_type}"

    @property
    def name(self) -> Optional[str]:
        return f"{self.serial_number} {self.heater_type.title()}"

    @property
    def temperature_unit(self):
        measurement_system = self.appliance.get_erd_value(ErdCode.TEMPERATURE_UNIT)
        if measurement_system == ErdMeasurementUnits.METRIC:
            return TEMP_CELSIUS
        return TEMP_FAHRENHEIT

    @property
    def supported_features(self):
        raise NotImplementedError

    @property
    def other_state_attrs(self) -> Dict[str, Any]:
        """State attributes to be optionally overridden in subclasses."""
        return {}

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        other_attrs = self.other_state_attrs
        return {**other_attrs}

    async def async_set_sabbath_mode(self, sabbath_on: bool = True):
        """Set sabbath mode if it's changed"""
        if self.appliance.get_erd_value(ErdCode.SABBATH_MODE) == sabbath_on:
            return
        await self.appliance.async_set_erd_value(ErdCode.SABBATH_MODE, sabbath_on)
