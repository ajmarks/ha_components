import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gehomesdk import (
    ErdCode, 
    ErdApplianceType
)

from .base import ApplianceApi
from ..entities import (
    GeErdBinarySensor,
    GeErdButton
)

_LOGGER = logging.getLogger(__name__)


class EspressoMakerApi(ApplianceApi):
    """API class for Espresso Maker objects"""
    APPLIANCE_TYPE = ErdApplianceType.ESPRESSO_MAKER

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()

        em_entities = [                   
            GeErdBinarySensor(self, ErdCode.CCM_IS_DESCALING),
            GeErdButton(self, ErdCode.CCM_CANCEL_DESCALING),
            GeErdButton(self, ErdCode.CCM_START_DESCALING),
            GeErdBinarySensor(self, ErdCode.CCM_OUT_OF_WATER, device_class_override="problem"),
        ]

        entities = base_entities + em_entities
        return entities
