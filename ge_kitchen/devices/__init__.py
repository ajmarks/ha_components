import logging
from typing import Type

from gekitchen.erd import ErdApplianceType

from .base import ApplianceApi
from .oven import OvenApi
from .fridge import FridgeApi
from .dishwasher import DishwasherApi

_LOGGER = logging.getLogger(__name__)

def get_appliance_api_type(appliance_type: ErdApplianceType) -> Type:
    _LOGGER.debug(f"Found device type: {appliance_type}")
    """Get the appropriate appliance type"""
    if appliance_type == ErdApplianceType.OVEN:
        return OvenApi
    if appliance_type == ErdApplianceType.FRIDGE:
        return FridgeApi
    if appliance_type == ErdApplianceType.DISH_WASHER:
        return DishwasherApi
    # Fallback
    return ApplianceApi
