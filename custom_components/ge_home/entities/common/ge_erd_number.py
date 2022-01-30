import logging
from typing import Optional
from gehomesdk.erd.erd_data_type import ErdDataType
from homeassistant.components.number import NumberEntity

from homeassistant.const import (
    DEVICE_CLASS_TEMPERATURE,
)
from gehomesdk import ErdCodeType, ErdCodeClass, ErdMeasurementUnits
from .ge_erd_entity import GeErdEntity
from ...devices import ApplianceApi
from ...const import TEMP_CELSIUS, TEMP_FAHRENHEIT

_LOGGER = logging.getLogger(__name__)

class GeErdNumber(GeErdEntity, NumberEntity):
    """GE Entity for numbers"""

    def __init__(
        self, 
        api: ApplianceApi, 
        erd_code: ErdCodeType, 
        erd_override: str = None, 
        icon_override: str = None, 
        device_class_override: str = None,
        uom_override: str = None,
        data_type_override: ErdDataType = None,
        min_value: float = 1,
        max_value: float = 100,
        step_value: float = 1,
        mode: str = "auto"
    ):
        super().__init__(api, erd_code, erd_override, icon_override, device_class_override)
        self._uom_override = uom_override
        self._data_type_override = data_type_override
        self._min_value = min_value
        self._max_value = max_value
        self._step_value = step_value
        self._mode = mode

    @property
    def value(self):
        try:
            value = self.appliance.get_erd_value(self.erd_code)
            return self._convert_value_from_device(value)
        except KeyError:
            return None

    @property
    def unit_of_measurement(self) -> Optional[str]:
        return self._get_uom()

    @property
    def _data_type(self) -> ErdDataType:
        if self._data_type_override is not None:
            return self._data_type_override

        return self.appliance.get_erd_code_data_type(self.erd_code)

    @property
    def min_value(self) -> float:
        return self._convert_value_from_device(self._min_value)

    @property
    def max_value(self) -> float:
        return self._convert_value_from_device(self._max_value)

    @property
    def step(self) -> float:
        return self._step_value

    @property
    def mode(self) -> float:
        return self._mode

    def _convert_value_from_device(self, value):
        """Convert to expected temperature units and data type"""
        
        if (self._get_uom() == TEMP_CELSIUS):
             # Convert to Celcius
            value = (value - 32 ) * 5/9

        if self._data_type == ErdDataType.INT:
            return int(round(value))
        else:
            return value

    def _get_uom(self):
        """Select appropriate units"""
        
        #if we have an override, just use it
        if self._uom_override:
            return self._uom_override

        if self.device_class == DEVICE_CLASS_TEMPERATURE:
            if self._measurement_system == ErdMeasurementUnits.METRIC:

                # Actual data from API is always in Fahrenhreit but since Device preferences are set to Celcius
                # we return Celcius here and will do the conversion ourselves
                return TEMP_CELSIUS
            else:
                return TEMP_FAHRENHEIT
        
        return None

    def _get_device_class(self) -> Optional[str]:
        if self._device_class_override:
            return self._device_class_override
        
        if self.erd_code_class in [
            ErdCodeClass.RAW_TEMPERATURE,
            ErdCodeClass.NON_ZERO_TEMPERATURE,
        ]:
            return DEVICE_CLASS_TEMPERATURE

        return None

    def _get_icon(self):
        if self.erd_code_class == ErdCodeClass.DOOR:
            if self.state.lower().endswith("open"):
                return "mdi:door-open"
            if self.state.lower().endswith("closed"):
                return "mdi:door-closed"
        return super()._get_icon()

    async def async_set_value(self, value):
        """Sets the ERD value, assumes that the data type is correct"""

        if self._get_uom() == TEMP_CELSIUS:
            # Convert to Fahrenheit
            value = (value * 9/5) + 32

        if self._data_type == ErdDataType.INT:
            value = int(round(value))

        try:
            await self.appliance.async_set_erd_value(self.erd_code, value) 
        except:
            _LOGGER.warning(f"Could not set {self.name} to {value}")