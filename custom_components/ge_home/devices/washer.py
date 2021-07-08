import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gehomesdk import ErdCode, ErdApplianceType

from .base import ApplianceApi
from ..entities import GeErdSensor, GeErdBinarySensor

_LOGGER = logging.getLogger(__name__)


class WasherApi(ApplianceApi):
    """API class for washer objects"""
    APPLIANCE_TYPE = ErdApplianceType.WASHER

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()

        common_entities = [
            GeErdSensor(self, ErdCode.LAUNDRY_MACHINE_STATE),
            GeErdSensor(self, ErdCode.LAUNDRY_CYCLE),
            GeErdSensor(self, ErdCode.LAUNDRY_SUB_CYCLE),
            GeErdBinarySensor(self, ErdCode.LAUNDRY_END_OF_CYCLE),
            GeErdSensor(self, ErdCode.LAUNDRY_TIME_REMAINING),
            GeErdSensor(self, ErdCode.LAUNDRY_DELAY_TIME_REMAINING),
            GeErdBinarySensor(self, ErdCode.LAUNDRY_DOOR),
            GeErdBinarySensor(self, ErdCode.LAUNDRY_REMOTE_STATUS),
        ]

        washer_entities = self.get_washer_entities()      

        entities = base_entities + common_entities + washer_entities
        return entities
        
    def get_washer_entities(self) -> List[Entity]:
        washer_entities = [         
            GeErdSensor(self, ErdCode.LAUNDRY_WASHER_SOIL_LEVEL),
            GeErdSensor(self, ErdCode.LAUNDRY_WASHER_WASHTEMP_LEVEL),
            GeErdSensor(self, ErdCode.LAUNDRY_WASHER_SPINTIME_LEVEL),
            GeErdSensor(self, ErdCode.LAUNDRY_WASHER_RINSE_OPTION),
        ]

        if self.has_erd_code(ErdCode.LAUNDRY_WASHER_DOOR_LOCK):
            washer_entities.extend([GeErdBinarySensor(self, ErdCode.LAUNDRY_WASHER_DOOR_LOCK)])
        if self.has_erd_code(ErdCode.LAUNDRY_WASHER_TANK_STATUS):
            washer_entities.extend([GeErdSensor(self, ErdCode.LAUNDRY_WASHER_TANK_STATUS)])           
        if self.has_erd_code(ErdCode.LAUNDRY_WASHER_TANK_SELECTED):
            washer_entities.extend([GeErdSensor(self, ErdCode.LAUNDRY_WASHER_TANK_SELECTED)])
        
        return washer_entities
