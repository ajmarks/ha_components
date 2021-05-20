import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gehomesdk.erd import ErdCode, ErdApplianceType

from .base import ApplianceApi
from ..entities import GeErdSensor, GeDishwasherControlLockedSwitch

_LOGGER = logging.getLogger(__name__)


class DishwasherApi(ApplianceApi):
    """API class for dishwasher objects"""
    APPLIANCE_TYPE = ErdApplianceType.WASHER

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()

        dishwasher_entities = [
            #GeDishwasherControlLockedSwitch(self, ErdCode.USER_INTERFACE_LOCKED),
            GeErdSensor(self, ErdCode.DISHWASHER_CYCLE_NAME),
            GeErdSensor(self, ErdCode.DISHWASHER_CYCLE_STATE),
            GeErdSensor(self, ErdCode.DISHWASHER_OPERATING_MODE),
            GeErdSensor(self, ErdCode.DISHWASHER_PODS_REMAINING_VALUE),
            GeErdSensor(self, ErdCode.DISHWASHER_RINSE_AGENT, icon_override="mdi:sparkles"),
            GeErdSensor(self, ErdCode.DISHWASHER_TIME_REMAINING),
        ]
        entities = base_entities + dishwasher_entities
        return entities
        
