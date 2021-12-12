"""GE Home Sensor Entities - Advantium"""
import logging
from typing import Any, Dict, List, Mapping, Optional, Set
from random import randrange

from gehomesdk import (
    ErdCode,
    ErdUnitType,
    ErdCcmBrewSettings, 
    ErdCcmBrewStrength   
)

from homeassistant.const import ATTR_TEMPERATURE

from ...const import DOMAIN
from ...devices import ApplianceApi
from ..common import GeWaterHeater
from .const import *
from .ge_ccm_options import CcmBrewOptionsConverter

_LOGGER = logging.getLogger(__name__)

class GeCcm(GeWaterHeater):
    """GE Appliance Cafe Coffee Maker"""

    icon = "mdi:coffee-maker"

    def __init__(self, api: ApplianceApi):
        super().__init__(api)
        self._options = CcmBrewOptionsConverter()

    @property
    def supported_features(self):
        return GE_CCM

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}_{self.serial_number}"

    @property
    def name(self) -> Optional[str]:
        return f"{self.serial_number} Coffee Maker"

    @property
    def unit_type(self) -> Optional[ErdUnitType]:
        try:
            return self.appliance.get_erd_value(ErdCode.UNIT_TYPE)
        except:
            return None

    @property
    def current_temperature(self) -> Optional[int]:
        return self.appliance.get_erd_value(ErdCode.CCM_CURRENT_WATER_TEMPERATURE)

    @property
    def is_brewing(self) -> bool:
        return self.appliance.get_erd_value(ErdCode.CCM_IS_BREWING)
    
    @property
    def is_descaling(self) -> bool:
        return self.appliance.get_erd_value(ErdCode.CCM_IS_DESCALING)

    @property
    def current_operation(self) -> Optional[str]:
        try:
            settings: ErdCcmBrewSettings = self.appliance.get_erd_value(ErdCode.CCM_BREW_SETTINGS)
            if self.is_descaling:
                return "Descale"
            if not self.is_brewing:
                return "Off"
            return self._options.to_option_string(settings)
        except:
            return None

    @property
    def operation_list(self) -> List[str]:
        return self._options.options

    @property
    def current_brew_setting(self) -> ErdCcmBrewSettings:
        """Get the current brew setting."""
        return self.appliance.get_erd_value(ErdCode.CCM_BREW_SETTINGS)

    @property
    def target_temperature(self) -> Optional[int]:
        """Return the temperature we try to reach."""
        try:
            return self.appliance.get_erd_value(ErdCode.CCM_BREW_TEMPERATURE)
        except:
            pass
        return None

    @property
    def min_temp(self) -> int:
        """Return the minimum temperature."""
        min_temp, _, _ = self.appliance.get_erd_value(ErdCode.CCM_BREW_TEMPERATURE_RANGE)
        return min_temp

    @property
    def max_temp(self) -> int:
        """Return the maximum temperature."""
        _, max_temp, _ = self.appliance.get_erd_value(ErdCode.CCM_BREW_TEMPERATURE_RANGE)
        return max_temp

    @property
    def extra_state_attributes(self) -> Optional[Mapping[str, Any]]:
        data = {}

        data["unit_type"] = self._stringify(self.unit_type)

        return data

    @property
    def can_set_temperature(self) -> bool:
        """Indicates whether we can set the temperature based on the current mode"""          
        return not self.is_descaling

    async def async_set_operation_mode(self, operation_mode: str):
        """Set the operation mode."""

        #try to get the mode/setting for the selection
        try:
            if operation_mode not in ["Off","Descale"]:
                new_mode = self._options.from_option_string(operation_mode)
                new_mode.brew_temperature = self.target_temperature

                await self.appliance.async_set_erd_value(ErdCode.CCM_BREW_SETTINGS, new_mode)
            elif operation_mode == "Off":
                await self.appliance.async_set_erd_value(ErdCode.CCM_CANCEL_BREWING, True)
                await self.appliance.async_set_erd_value(ErdCode.CCM_CANCEL_DESCALING, True)
            elif operation_mode == "Descale":
                await self.appliance.async_set_erd_value(ErdCode.CCM_START_DESCALING, True)
        except:
            _LOGGER.debug(f"Error Attempting to set mode to {operation_mode}.")

    async def async_set_temperature(self, **kwargs):
        """Set the brew temperature"""

        target_temp = kwargs.get(ATTR_TEMPERATURE)
        if target_temp is None:
            return

        # get the current strength/cups
        strength: ErdCcmBrewStrength = self.appliance.get_erd_value(ErdCode.CCM_BREW_STRENGTH)
        cups: int = self.appliance.get_erd_value(ErdCode.CCM_BREW_CUPS)
        new_mode = ErdCcmBrewSettings(cups, strength, target_temp)

        await self.appliance.async_set_erd_value(ErdCode.CCM_BREW_SETTINGS, new_mode)            

