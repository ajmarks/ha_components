import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gekitchensdk.erd import ErdCode, ErdApplianceType

from .base import ApplianceApi
from ..entities import GeErdSensor, GeDishwasherControlLockedSwitch

_LOGGER = logging.getLogger(__name__)


class DryerApi(ApplianceApi):
    """API class for dryer objects"""
    APPLIANCE_TYPE = ErdApplianceType.WASHER

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()

        dryer_entities = [

        ]
        entities = base_entities + dryer_entities
        return entities
        