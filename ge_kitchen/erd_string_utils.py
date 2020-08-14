"""Utilities to make nice strings from ERD values."""

from gekitchen.erd_types import OvenCookSetting
from gekitchen.erd_constants import ErdOvenState
from .erd_constants.oven_constants import (
    OVEN_DISPLAY_STATE_MAP,
    STATE_OVEN_DELAY,
    STATE_OVEN_PROBE,
    STATE_OVEN_SABBATH,
    STATE_OVEN_TIMED,
    STATE_OVEN_UNKNOWN,
)


def oven_display_state_to_str(oven_state: ErdOvenState) -> str:
    """Translate ErdOvenState values to a nice constant."""
    return OVEN_DISPLAY_STATE_MAP.get(oven_state, STATE_OVEN_UNKNOWN)


def oven_cook_setting_to_str(cook_setting: OvenCookSetting, units: str) -> str:
    """Format OvenCookSetting values nicely."""
    cook_mode = cook_setting.cook_mode
    cook_state = cook_mode.oven_state
    temperature = cook_setting.temperature

    modifiers = []
    if cook_mode.timed:
        modifiers.append(STATE_OVEN_TIMED)
    if cook_mode.delayed:
        modifiers.append(STATE_OVEN_DELAY)
    if cook_mode.probe:
        modifiers.append(STATE_OVEN_PROBE)
    if cook_mode.sabbath:
        modifiers.append(STATE_OVEN_SABBATH)

    temp_str = f" ({temperature}{units})" if temperature > 0 else ""
    modifier_str = f" ({', '.join(modifiers)})" if modifiers else ""
    display_state = oven_display_state_to_str(cook_state)
    return f"{display_state}{temp_str}{modifier_str}"
