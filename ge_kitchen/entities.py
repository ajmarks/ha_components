"""Define all of the entity types"""

import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

from gekitchen import ErdCodeType, GeAppliance, translate_erd_code
from gekitchen.erd_types import *
from gekitchen.erd_constants import *
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.core import HomeAssistant


from .const import DOMAIN
from .erd_string_utils import *

if TYPE_CHECKING:
    from .appliance_api import ApplianceApi


_LOGGER = logging.getLogger(__name__)

DOOR_ERD_CODES = {
    ErdCode.DOOR_STATUS
}
RAW_TEMPERATURE_ERD_CODES = {
    ErdCode.LOWER_OVEN_RAW_TEMPERATURE,
    ErdCode.LOWER_OVEN_USER_TEMP_OFFSET,
    ErdCode.UPPER_OVEN_RAW_TEMPERATURE,
    ErdCode.UPPER_OVEN_USER_TEMP_OFFSET,
    ErdCode.CURRENT_TEMPERATURE,
    ErdCode.TEMPERATURE_SETTING,
}
NONZERO_TEMPERATURE_ERD_CODES = {
    ErdCode.HOT_WATER_SET_TEMP,
    ErdCode.LOWER_OVEN_DISPLAY_TEMPERATURE,
    ErdCode.LOWER_OVEN_PROBE_DISPLAY_TEMP,
    ErdCode.UPPER_OVEN_DISPLAY_TEMPERATURE,
    ErdCode.UPPER_OVEN_PROBE_DISPLAY_TEMP,
}
TEMPERATURE_ERD_CODES = RAW_TEMPERATURE_ERD_CODES.union(NONZERO_TEMPERATURE_ERD_CODES)
TIMER_ERD_CODES = {
    ErdCode.LOWER_OVEN_ELAPSED_COOK_TIME,
    ErdCode.LOWER_OVEN_KITCHEN_TIMER,
    ErdCode.LOWER_OVEN_DELAY_TIME_REMAINING,
    ErdCode.LOWER_OVEN_COOK_TIME_REMAINING,
    ErdCode.LOWER_OVEN_ELAPSED_COOK_TIME,
    ErdCode.ELAPSED_ON_TIME,
    ErdCode.TIME_REMAINING,
    ErdCode.UPPER_OVEN_ELAPSED_COOK_TIME,
    ErdCode.UPPER_OVEN_KITCHEN_TIMER,
    ErdCode.UPPER_OVEN_DELAY_TIME_REMAINING,
    ErdCode.UPPER_OVEN_ELAPSED_COOK_TIME,
    ErdCode.UPPER_OVEN_COOK_TIME_REMAINING,
}


def boolify_erd_value(erd_code: ErdCodeType, value: Any) -> Optional[bool]:
    """
    Convert an erd property value to a bool

    :param erd_code: The ERD code for the property
    :param value: The current value in its native format
    :return: The value converted to a bool
    """
    erd_code = translate_erd_code(erd_code)
    if isinstance(value, ErdDoorStatus):
        if value == ErdDoorStatus.NA:
            return None
        return value == ErdDoorStatus.OPEN
    if value is None:
        return None
    return bool(value)


def stringify_erd_value(erd_code: ErdCodeType, value: Any, units: Optional[str] = None) -> Optional[str]:
    """
    Convert an erd property value to a nice string

    :param erd_code: The ERD code for the property
    :param value: The current value in its native format
    :param units: Units to apply, if applicable
    :return: The value converted to a string
    """
    erd_code = translate_erd_code(erd_code)

    if isinstance(value, ErdOvenState):
        return oven_display_state_to_str(value)
    if isinstance(value, OvenCookSetting):
        return oven_cook_setting_to_str(value, units)
    if isinstance(value, FridgeDoorStatus):
        return value.status
    if isinstance(value, FridgeIceBucketStatus):
        return bucket_status_to_str(value)
    if isinstance(value, ErdFilterStatus):
        return value.name.capitalize()
    if isinstance(value, HotWaterStatus):
        return hot_water_status_str(value)
    if isinstance(value, ErdDoorStatus):
        return door_status_to_str(value)

    if erd_code == ErdCode.CLOCK_TIME:
        return value.strftime("%H:%M:%S") if value else None
    if erd_code in RAW_TEMPERATURE_ERD_CODES:
        return f"{value}"
    if erd_code in NONZERO_TEMPERATURE_ERD_CODES:
        return f"{value}" if value else ""
    if erd_code in TIMER_ERD_CODES:
        return str(value)[:-3] if value else ""
    if erd_code == ErdCode.DOOR_STATUS:
        return value.status
    if value is None:
        return None
    return str(value)


def get_erd_units(erd_code: ErdCodeType, measurement_units: ErdMeasurementUnits):
    """Get the units for a sensor."""
    erd_code = translate_erd_code(erd_code)
    if not measurement_units:
        return None

    if erd_code in TEMPERATURE_ERD_CODES or erd_code in {ErdCode.LOWER_OVEN_COOK_MODE, ErdCode.UPPER_OVEN_COOK_MODE}:
        if measurement_units == ErdMeasurementUnits.METRIC:
            return TEMP_CELSIUS
        return TEMP_FAHRENHEIT
    return None


def get_erd_icon(erd_code: ErdCodeType, value: Any = None) -> Optional[str]:
    """Select an appropriate icon."""
    erd_code = translate_erd_code(erd_code)
    if not isinstance(erd_code, ErdCode):
        return None
    if erd_code in TIMER_ERD_CODES:
        return "mdi:timer-outline"
    if erd_code in {
        ErdCode.LOWER_OVEN_COOK_MODE,
        ErdCode.LOWER_OVEN_CURRENT_STATE,
        ErdCode.LOWER_OVEN_WARMING_DRAWER_STATE,
        ErdCode.UPPER_OVEN_COOK_MODE,
        ErdCode.UPPER_OVEN_CURRENT_STATE,
        ErdCode.UPPER_OVEN_WARMING_DRAWER_STATE,
        ErdCode.WARMING_DRAWER_STATE,
    }:
        return "mdi:stove"
    if erd_code in {
        ErdCode.TURBO_COOL_STATUS,
        ErdCode.TURBO_FREEZE_STATUS,
    }:
        return "mdi:snowflake"
    if erd_code == ErdCode.SABBATH_MODE:
        return "mdi:judaism"

    # Let binary sensors assign their own.  Might be worth passing
    # the actual entity in if we want to do more of this.
    if erd_code in DOOR_ERD_CODES and isinstance(value, str):
        if "open" in value.lower():
            return "mdi:door-open"
        return "mdi:door-closed"

    return None


class GeEntity:
    """Base class for all GE Entities"""
    should_poll = False

    def __init__(self, api: "ApplianceApi"):
        self._api = api
        self.hass = None  # type: Optional[HomeAssistant]

    @property
    def unique_id(self) -> str:
        raise NotImplementedError

    @property
    def api(self) -> "ApplianceApi":
        return self._api

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self.api.device_info

    @property
    def serial_number(self):
        return self.api.serial_number

    @property
    def available(self) -> bool:
        return self.appliance.available

    @property
    def appliance(self) -> GeAppliance:
        return self.api.appliance

    @property
    def name(self) -> Optional[str]:
        raise NotImplementedError


class GeErdEntity(GeEntity):
    """Parent class for GE entities tied to a specific ERD"""
    def __init__(self, api: "ApplianceApi", erd_code: ErdCodeType):
        super().__init__(api)
        self._erd_code = translate_erd_code(erd_code)

    @property
    def erd_code(self) -> ErdCodeType:
        return self._erd_code

    @property
    def erd_string(self) -> str:
        erd_code = self.erd_code
        if isinstance(self.erd_code, ErdCode):
            return erd_code.name
        return erd_code

    @property
    def name(self) -> Optional[str]:
        erd_string = self.erd_string
        erd_title = " ".join(erd_string.split("_")).title()
        return f"{self.appliance.serial_number} {erd_title}"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{DOMAIN}_{self.serial_number}_{self.erd_string.lower()}"

    @property
    def icon(self) -> Optional[str]:
        return get_erd_icon(self.erd_code)
