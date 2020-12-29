from typing import Optional

from homeassistant.const import DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.helpers.entity import Entity
from gekitchen import ErdCode, ErdCodeClass, ErdMeasurementUnits

from .ge_erd_entity import GeErdEntity

class GeErdSensor(GeErdEntity, Entity):  
    """GE Entity for sensors"""
    @property
    def state(self) -> Optional[str]:
        try:
            value = self.appliance.get_erd_value(self.erd_code)
        except KeyError:
            return None
        return self._stringify(value, units=self.units)

    @property
    def measurement_system(self) -> Optional[ErdMeasurementUnits]:
        try:
            value = self.appliance.get_erd_value(ErdCode.TEMPERATURE_UNIT)
        except KeyError:
            return None
        return value

    @property
    def units(self) -> Optional[str]:
        return get_erd_units(self.erd_code, self.measurement_system)

    @property
    def device_class(self) -> Optional[str]:
        if self.erd_code_class in [ErdCodeClass.RAW_TEMPERATURE, ErdCodeClass.NON_ZERO_TEMPERATURE]:
            return DEVICE_CLASS_TEMPERATURE
        return None

    @property
    def icon(self) -> Optional[str]:
        return get_erd_icon(self.erd_code, self.state)

    @property
    def unit_of_measurement(self) -> Optional[str]:
        if self.device_class == DEVICE_CLASS_TEMPERATURE:
            return self.units
