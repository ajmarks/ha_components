from homeassistant.components.binary_sensor import DEVICE_CLASS_PROBLEM
from homeassistant.const import DEVICE_CLASS_TEMPERATURE
import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gekitchen.erd import ErdCode, ErdApplianceType

from .base import ApplianceApi
from ..entities import (
    GeErdSensor, 
    GeErdSwitch, 
    GeFridge, 
    GeFreezer, 
    GeDispenser, 
    GeErdPropertySensor,
    GeErdPropertyBinarySensor
)

_LOGGER = logging.getLogger(__name__)

class FridgeApi(ApplianceApi):
    """API class for oven objects"""
    APPLIANCE_TYPE = ErdApplianceType.FRIDGE

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()
    
        fridge_entities = []
        freezer_entities = []
        dispenser_entities = []

        common_entities = [
            GeErdSensor(self, ErdCode.FRIDGE_MODEL_INFO),
            GeErdSwitch(self, ErdCode.SABBATH_MODE),
            GeErdSensor(self, ErdCode.DOOR_STATUS),
            GeErdPropertyBinarySensor(self, ErdCode.DOOR_STATUS, "any_open")
        ]

        fridge_entities.extend([
            GeErdSensor(self, ErdCode.WATER_FILTER_STATUS),
            GeErdPropertySensor(self, ErdCode.CURRENT_TEMPERATURE, "fridge"),
            GeFridge(self),
        ])

        freezer_entities.extend([
            GeErdPropertySensor(self, ErdCode.CURRENT_TEMPERATURE, "freezer"),
            GeFreezer(self),                  
        ])

        dispenser_entities.extend([
            GeErdSensor(self, ErdCode.HOT_WATER_IN_USE),
            GeErdSensor(self, ErdCode.HOT_WATER_SET_TEMP),
            GeErdPropertySensor(self, ErdCode.HOT_WATER_STATUS, "status"),
            GeErdPropertySensor(self, ErdCode.HOT_WATER_STATUS, "time_remaining", icon_override="mdi:timer-outline"),
            GeErdPropertySensor(self, ErdCode.HOT_WATER_STATUS, "time_remaining", device_class_override=DEVICE_CLASS_TEMPERATURE),
            GeErdPropertyBinarySensor(self, ErdCode.HOT_WATER_STATUS, "faulted", device_class_override=DEVICE_CLASS_PROBLEM),
            GeDispenser(self)
        ])

        entities = base_entities + common_entities + fridge_entities + freezer_entities + dispenser_entities
        return entities
