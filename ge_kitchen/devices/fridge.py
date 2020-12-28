import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gekitchen.erd import ErdCode, ErdApplianceType

from .base import ApplianceApi
from ..entities import GeErdSensor, GeErdSwitch, GeFridgeEntity, GeFreezerEntity

_LOGGER = logging.getLogger(__name__)

class FridgeApi(ApplianceApi):
    """API class for oven objects"""
    APPLIANCE_TYPE = ErdApplianceType.FRIDGE

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()

        fridge_entities = [
            GeErdSensor(self, ErdCode.AIR_FILTER_STATUS),
            GeErdSensor(self, ErdCode.DOOR_STATUS),
            GeErdSensor(self, ErdCode.FRIDGE_MODEL_INFO),
            GeErdSensor(self, ErdCode.HOT_WATER_IN_USE),
            GeErdSensor(self, ErdCode.HOT_WATER_SET_TEMP),
            GeErdSensor(self, ErdCode.HOT_WATER_STATUS),
            GeErdSwitch(self, ErdCode.SABBATH_MODE),
            GeFreezerEntity(self),
            GeFridgeEntity(self),
        ]
        entities = base_entities + fridge_entities
        return entities
