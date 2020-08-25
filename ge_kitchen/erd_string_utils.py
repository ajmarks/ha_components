"""Utilities to make nice strings from ERD values."""

__all__ = (
    "hot_water_status_str",
    "oven_display_state_to_str",
    "oven_cook_setting_to_str",
    "bucket_status_to_str",
    "door_status_to_str",
)

from typing import Optional

from gekitchen.erd_types import OvenCookSetting, FridgeIceBucketStatus, HotWaterStatus
from gekitchen.erd_constants import ErdOvenState, ErdFullNotFull, ErdDoorStatus
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


def bucket_status_to_str(bucket_status: FridgeIceBucketStatus) -> str:
    status = bucket_status.total_status
    if status == ErdFullNotFull.FULL:
        return "Full"
    if status == ErdFullNotFull.NOT_FULL:
        return "Not Full"
    if status == ErdFullNotFull.NA:
        return "NA"


def hot_water_status_str(water_status: HotWaterStatus) -> str:
    raise NotImplementedError


def door_status_to_str(door_status: ErdDoorStatus) -> Optional[str]:
    if door_status == ErdDoorStatus.NA:
        return None
    return door_status.name.title()
