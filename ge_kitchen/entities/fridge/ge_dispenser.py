"""GE Kitchen Sensor Entities - Dispenser"""

import logging
from typing import List, Optional

from gekitchen import (
    ErdCode,
    ErdPresent,
    ErdPodStatus,
    HotWaterStatus
)

from ..common import GeWaterHeater
from .const import (
    HEATER_TYPE_DISPENSER, OP_MODE_K_CUP,
    OP_MODE_NORMAL,
    OP_MODE_SABBATH
)

_LOGGER = logging.getLogger(__name__)

class GeDispenser(GeWaterHeater):
    """Entity for in-fridge dispensers"""
    
    # These values are from FridgeHotWaterFragment.smali in the android app
    min_temp = 90
    max_temp = 185

    heater_type = HEATER_TYPE_DISPENSER

    @property
    def hot_water_status(self) -> HotWaterStatus:
        """Access the main status value conveniently."""
        return self.appliance.get_erd_value(ErdCode.HOT_WATER_STATUS)

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
