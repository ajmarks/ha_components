import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gekitchen.erd import ErdCode, ErdApplianceType, OvenConfiguration

from .base import ApplianceApi
from ..entities import GeErdSensor, GeErdBinarySensor, GeOvenHeaterEntity

_LOGGER = logging.getLogger(__name__)

class OvenApi(ApplianceApi):
    """API class for oven objects"""
    APPLIANCE_TYPE = ErdApplianceType.OVEN

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()
        oven_config: OvenConfiguration = self.appliance.get_erd_value(ErdCode.OVEN_CONFIGURATION)
        _LOGGER.debug(f"Oven Config: {oven_config}")
        oven_entities = []

        if oven_config.has_lower_oven:
            oven_entities.extend([
                GeErdSensor(self, ErdCode.UPPER_OVEN_COOK_MODE),
                GeErdSensor(self, ErdCode.UPPER_OVEN_COOK_TIME_REMAINING),
                GeErdSensor(self, ErdCode.UPPER_OVEN_KITCHEN_TIMER),
                GeErdSensor(self, ErdCode.UPPER_OVEN_USER_TEMP_OFFSET),
                GeErdBinarySensor(self, ErdCode.UPPER_OVEN_REMOTE_ENABLED),

                GeErdSensor(self, ErdCode.LOWER_OVEN_COOK_MODE),
                GeErdSensor(self, ErdCode.LOWER_OVEN_COOK_TIME_REMAINING),
                GeErdSensor(self, ErdCode.LOWER_OVEN_USER_TEMP_OFFSET),
                GeErdBinarySensor(self, ErdCode.LOWER_OVEN_REMOTE_ENABLED),
                GeOvenHeaterEntity(self, LOWER_OVEN, True),
                GeOvenHeaterEntity(self, UPPER_OVEN, True),
            ])
        else:
            oven_entities.extend([
                GeErdSensor(self, ErdCode.UPPER_OVEN_COOK_MODE, "Oven Cook Mode"),
                GeErdSensor(self, ErdCode.UPPER_OVEN_COOK_TIME_REMAINING, "Oven Cook Time Remaining"),
                GeErdSensor(self, ErdCode.UPPER_OVEN_KITCHEN_TIMER, "Oven Kitchen Timer"),
                GeErdSensor(self, ErdCode.UPPER_OVEN_USER_TEMP_OFFSET, "Oven User Temp Offset"),
                GeErdBinarySensor(self, ErdCode.UPPER_OVEN_REMOTE_ENABLED, "Oven Remote Enabled"),
                GeOvenHeaterEntity(self, UPPER_OVEN, False)
            ])
        return base_entities + oven_entities
