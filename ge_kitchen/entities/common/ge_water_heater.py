import abc
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.water_heater import WaterHeaterEntity
from homeassistant.const import (
    TEMP_FAHRENHEIT,
    TEMP_CELSIUS
)
from gekitchensdk import ErdCode, ErdMeasurementUnits
from ge_kitchen.const import DOMAIN
from .ge_erd_entity import GeEntity

_LOGGER = logging.getLogger(__name__)

class GeWaterHeater(GeEntity, WaterHeaterEntity, metaclass=abc.ABCMeta):
    """Mock temperature/operation mode supporting device as a water heater"""

    @property
    def available(self) -> bool:
        available = super().available
        if not available:
            app = self.appliance
            _LOGGER.critical(f"{self.name} unavailable. Appliance info: Available - {app._available} and Init - {app.initialized}")
        return available

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
