import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gekitchen.erd import ErdCode, ErdApplianceType

from .base import ApplianceApi
from ..entities import GeErdSensor, GeErdSwitch, GeFridgeEntity, GeFreezerEntity

_LOGGER = logging.getLogger(__name__)


class DishwasherApi(ApplianceApi):
    """API class for oven objects"""
    APPLIANCE_TYPE = ErdApplianceType.DISH_WASHER

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()

        dishwasher_entities = [
            GeErdSensor(self, ErdCode.CYCLE_NAME),
            GeErdSensor(self, ErdCode.CYCLE_STATE),
            GeErdSensor(self, ErdCode.OPERATING_MODE),
            GeErdSensor(self, ErdCode.PODS_REMAINING_VALUE),
            GeErdSensor(self, ErdCode.RINSE_AGENT),
            GeErdSensor(self, ErdCode.SOUND),
            GeErdSensor(self, ErdCode.TIME_REMAINING),
        ]
        entities = base_entities + dishwasher_entities
        return entities
        