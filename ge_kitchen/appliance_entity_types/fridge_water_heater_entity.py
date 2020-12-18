"""GE Kitchen Sensor Entities - Fridge Water Heater"""
import sys
import os
import abc
import async_timeout
from datetime import timedelta
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

sys.path.append(os.getcwd() + '/..')

from bidict import bidict
from gekitchen import (
    ErdCode,
    ErdPresent,
    ErdMeasurementUnits,
    ErdPodStatus
)
from gekitchen.erd_types import (
    HotWaterStatus
)

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT
from ..entities import GeEntity
from .abstract_fridge_entity import (
    OP_MODE_K_CUP,
    OP_MODE_NORMAL,
    OP_MODE_SABBATH,
    GeAbstractFridgeEntity
)

_LOGGER = logging.getLogger(__name__)

class GeFridgeWaterHeater(GeEntity, WaterHeaterEntity):
    """Entity for in-fridge water heaters"""

    # These values are from FridgeHotWaterFragment.smali in the android app
    min_temp = 90
    max_temp = 185

    @property
    def hot_water_status(self) -> HotWaterStatus:
        """Access the main status value conveniently."""
        return self.appliance.get_erd_value(ErdCode.HOT_WATER_STATUS)

    @property
    def unique_id(self) -> str:
        """Make a unique id."""
        return f"{self.serial_number}-fridge-hot-water"

    @property
    def name(self) -> Optional[str]:
        """Name it reasonably."""
        return f"GE Fridge Water Heater {self.serial_number}"

    @property
    def temperature_unit(self):
        """Select the appropriate temperature unit."""
        measurement_system = self.appliance.get_erd_value(ErdCode.TEMPERATURE_UNIT)
        if measurement_system == ErdMeasurementUnits.METRIC:
            return TEMP_CELSIUS
        return TEMP_FAHRENHEIT

    @property
    def supports_k_cups(self) -> bool:
        """Return True if the device supports k-cup brewing."""
        status = self.hot_water_status
        return status.pod_status != ErdPodStatus.NA and status.brew_module != ErdPresent.NA

    @property
    def operation_list(self) -> List[str]:
        """Supported Operations List"""
        ops_list = [OP_MODE_NORMAL, OP_MODE_SABBATH]
        if self.supports_k_cups:
            ops_list.append(OP_MODE_K_CUP)
        return ops_list

    async def async_set_temperature(self, **kwargs):
        pass

    async def async_set_operation_mode(self, operation_mode):
        pass

    @property
    def supported_features(self):
        pass

    @property
    def current_operation(self) -> str:
        """Get the current operation mode."""
        if self.appliance.get_erd_value(ErdCode.SABBATH_MODE):
            return OP_MODE_SABBATH
        return OP_MODE_NORMAL

    @property
    def current_temperature(self) -> Optional[int]:
        """Return the current temperature."""
        return self.hot_water_status.current_temp
