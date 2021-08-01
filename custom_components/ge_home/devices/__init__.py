import logging
from typing import Type

from gehomesdk.erd import ErdApplianceType

from .base import ApplianceApi
from .oven import OvenApi
from .fridge import FridgeApi
from .dishwasher import DishwasherApi
from .washer import WasherApi
from .dryer import DryerApi
from .washer_dryer import WasherDryerApi
from .water_filter import WaterFilterApi
from .advantium import AdvantiumApi

_LOGGER = logging.getLogger(__name__)


def get_appliance_api_type(appliance_type: ErdApplianceType) -> Type:
    """Get the appropriate appliance type"""
    _LOGGER.debug(f"Found device type: {appliance_type}")
    if appliance_type == ErdApplianceType.OVEN:
        return OvenApi
    if appliance_type == ErdApplianceType.FRIDGE:
        return FridgeApi
    if appliance_type == ErdApplianceType.DISH_WASHER:
        return DishwasherApi
    if appliance_type == ErdApplianceType.WASHER:
        return WasherApi
    if appliance_type == ErdApplianceType.DRYER:
        return DryerApi
    if appliance_type == ErdApplianceType.COMBINATION_WASHER_DRYER:
        return WasherDryerApi
    if appliance_type == ErdApplianceType.POE_WATER_FILTER:
        return WaterFilterApi
    if appliance_type == ErdApplianceType.ADVANTIUM:
        return AdvantiumApi

    # Fallback
    return ApplianceApi
