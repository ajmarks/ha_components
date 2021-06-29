from typing import Optional

from homeassistant.const import (
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_POWER_FACTOR,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
from homeassistant.helpers.entity import Entity
from gehomesdk import ErdCode, ErdCodeClass, ErdMeasurementUnits

from .ge_erd_entity import GeErdEntity


class GeErdSensor(GeErdEntity, Entity):
    """GE Entity for sensors"""

    @property
    def state(self) -> Optional[str]:
        try:
            value = self.appliance.get_erd_value(self.erd_code)
        except KeyError:
            return None
        # TODO: perhaps enhance so that there's a list of variables available
        #       for the stringify function to consume...
        return self._stringify(value, temp_units=self._temp_units)

    @property
    def unit_of_measurement(self) -> Optional[str]:
        return self._get_uom()

    @property
    def _temp_units(self) -> Optional[str]:
        if self._temp_measurement_system == ErdMeasurementUnits.METRIC:
            return TEMP_CELSIUS
        return TEMP_FAHRENHEIT

    def _get_uom(self):
        """Select appropriate units"""
        if (
            self.erd_code_class
            in [ErdCodeClass.RAW_TEMPERATURE, ErdCodeClass.NON_ZERO_TEMPERATURE]
            or self.device_class == DEVICE_CLASS_TEMPERATURE
        ):
            if self._temp_measurement_system == ErdMeasurementUnits.METRIC:
                return TEMP_CELSIUS
            return TEMP_FAHRENHEIT
        if (
            self.erd_code_class == ErdCodeClass.BATTERY
            or self.device_class == DEVICE_CLASS_BATTERY
        ):
            return "%"
        if self.device_class == DEVICE_CLASS_POWER_FACTOR:
            return "%"
        return None

    def _get_device_class(self) -> Optional[str]:
        if self._device_class_override:
            return self._device_class_override
        if self.erd_code_class in [
            ErdCodeClass.RAW_TEMPERATURE,
            ErdCodeClass.NON_ZERO_TEMPERATURE,
        ]:
            return DEVICE_CLASS_TEMPERATURE
        if self.erd_code_class == ErdCodeClass.BATTERY:
            return DEVICE_CLASS_BATTERY

        return None

    def _get_icon(self):
        if self.erd_code_class == ErdCodeClass.DOOR:
            if self.state.lower().endswith("open"):
                return "mdi:door-open"
            if self.state.lower().endswith("closed"):
                return "mdi:door-closed"
        return super()._get_icon()
