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



