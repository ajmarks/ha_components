from custom_components.ge_home.entities.advantium.ge_advantium import GeAdvantium
import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gehomesdk.erd import ErdCode, ErdApplianceType

from .base import ApplianceApi
from ..entities import GeErdSensor, GeErdBinarySensor, GeErdPropertySensor, GeErdPropertyBinarySensor, UPPER_OVEN

_LOGGER = logging.getLogger(__name__)

class AdvantiumApi(ApplianceApi):
    """API class for Advantium objects"""
    APPLIANCE_TYPE = ErdApplianceType.ADVANTIUM

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()

        advantium_entities = [
            GeErdSensor(self, ErdCode.UNIT_TYPE),
            GeErdBinarySensor(self, ErdCode.UPPER_OVEN_REMOTE_ENABLED, self._single_name(ErdCode.UPPER_OVEN_REMOTE_ENABLED)),
            GeErdBinarySensor(self, ErdCode.MICROWAVE_REMOTE_ENABLE),
            GeErdSensor(self, ErdCode.UPPER_OVEN_DISPLAY_TEMPERATURE, self._single_name(ErdCode.UPPER_OVEN_DISPLAY_TEMPERATURE)),
            GeErdSensor(self, ErdCode.ADVANTIUM_KITCHEN_TIME_REMAINING),
            GeErdSensor(self, ErdCode.ADVANTIUM_COOK_TIME_REMAINING),
            GeAdvantium(self),

            #Cook Status
            GeErdPropertySensor(self, ErdCode.ADVANTIUM_COOK_STATUS, "cook_mode"),
            GeErdPropertySensor(self, ErdCode.ADVANTIUM_COOK_STATUS, "termination_reason"),
            GeErdPropertySensor(self, ErdCode.ADVANTIUM_COOK_STATUS, "preheat_status"),
            GeErdPropertySensor(self, ErdCode.ADVANTIUM_COOK_STATUS, "temperature"),
            GeErdPropertySensor(self, ErdCode.ADVANTIUM_COOK_STATUS, "power_level"),
            GeErdPropertySensor(self, ErdCode.ADVANTIUM_COOK_STATUS, "warm_status"),
            GeErdPropertyBinarySensor(self, ErdCode.ADVANTIUM_COOK_STATUS, "door_status"),
            GeErdPropertyBinarySensor(self, ErdCode.ADVANTIUM_COOK_STATUS, "sensing_active"),
            GeErdPropertyBinarySensor(self, ErdCode.ADVANTIUM_COOK_STATUS, "cooling_fan_status"),
            GeErdPropertyBinarySensor(self, ErdCode.ADVANTIUM_COOK_STATUS, "oven_light_status"),
        ]
        entities = base_entities + advantium_entities
        return entities

    def _single_name(self, erd_code: ErdCode):
        return erd_code.name.replace(UPPER_OVEN+"_","").replace("_", " ").title()

