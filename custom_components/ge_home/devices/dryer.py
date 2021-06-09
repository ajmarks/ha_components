import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gehomesdk.erd import ErdCode, ErdApplianceType

from .base import ApplianceApi
from ..entities import GeErdSensor, GeErdBinarySensor

_LOGGER = logging.getLogger(__name__)


class DryerApi(ApplianceApi):
    """API class for dryer objects"""
    APPLIANCE_TYPE = ErdApplianceType.DRYER

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()

        dryer_entities = [
            GeErdSensor(self, ErdCode.LAUNDRY_MACHINE_STATE),
            GeErdSensor(self, ErdCode.LAUNDRY_MACHINE_SUBCYCLE),
            GeErdBinarySensor(self, ErdCode.LAUNDRY_END_OF_CYCLE),
            GeErdSensor(self, ErdCode.LAUNDRY_TIME_REMAINING),
            GeErdSensor(self, ErdCode.LAUNDRY_CYCLE),
            GeErdSensor(self, ErdCode.LAUNDRY_DELAY_TIME_REMAINING),
            GeErdSensor(self, ErdCode.LAUNDRY_DOOR),
            GeErdSensor(self, ErdCode.LAUNDRY_DRYNESSNEW_LEVEL),
            GeErdSensor(self, ErdCode.LAUNDRY_TEMPERATURENEW_OPTION),
            GeErdBinarySensor(self, ErdCode.LAUNDRY_REMOTE_STATUS)

        ]
        entities = base_entities + dryer_entities
        return entities
        
