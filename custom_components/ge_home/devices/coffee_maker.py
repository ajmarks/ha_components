import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gehomesdk import (
    ErdCode, 
    ErdApplianceType
)

from .base import ApplianceApi
from ..entities import (
    GeCcmPotNotPresentBinarySensor,
    GeErdSensor, 
    GeErdBinarySensor,
    GeCcm
)

_LOGGER = logging.getLogger(__name__)


class CcmApi(ApplianceApi):
    """API class for Cafe Coffee Maker objects"""
    APPLIANCE_TYPE = ErdApplianceType.CAFE_COFFEE_MAKER

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()

        units = self.hass.config.units

        ccm_entities = [
            GeErdBinarySensor(self, ErdCode.CCM_IS_BREWING, device_class_override="heat"),                        
            GeErdBinarySensor(self, ErdCode.CCM_IS_DESCALING),                        
            GeErdSensor(self, ErdCode.CCM_BREW_STRENGTH),
            GeErdSensor(self, ErdCode.CCM_BREW_CUPS),
            GeErdSensor(self, ErdCode.CCM_BREW_TEMPERATURE),
            GeErdSensor(self, ErdCode.CCM_CURRENT_WATER_TEMPERATURE),
            GeErdBinarySensor(self, ErdCode.CCM_OUT_OF_WATER, device_class_override="problem"),                        
            GeCcmPotNotPresentBinarySensor(self, ErdCode.CCM_POT_PRESENT, device_class_override="problem"),
            GeCcm(self, units)
        ]

        entities = base_entities + ccm_entities
        return entities
        
