import logging
from typing import List

from homeassistant.const import DEVICE_CLASS_POWER_FACTOR
from homeassistant.helpers.entity import Entity
from gehomesdk import (
    ErdCode, 
    ErdApplianceType, 
    OvenConfiguration, 
    ErdCooktopConfig, 
    CooktopStatus
)

from .base import ApplianceApi
from ..entities import (
    GeErdSensor, 
    GeErdBinarySensor, 
    GeErdPropertySensor,
    GeErdPropertyBinarySensor,
    GeOven, 
    UPPER_OVEN, 
    LOWER_OVEN
)

_LOGGER = logging.getLogger(__name__)

class OvenApi(ApplianceApi):
    """API class for oven objects"""
    APPLIANCE_TYPE = ErdApplianceType.OVEN

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()
        oven_config: OvenConfiguration = self.appliance.get_erd_value(ErdCode.OVEN_CONFIGURATION)

        cooktop_config = ErdCooktopConfig.NONE
        if self.has_erd_code(ErdCode.COOKTOP_CONFIG):
            cooktop_config: ErdCooktopConfig = self.appliance.get_erd_value(ErdCode.COOKTOP_CONFIG)

        _LOGGER.debug(f"Oven Config: {oven_config}")
        _LOGGER.debug(f"Cooktop Config: {cooktop_config}")
        oven_entities = []
        cooktop_entities = []

        if oven_config.has_lower_oven:
            oven_entities.extend([
                GeErdSensor(self, ErdCode.UPPER_OVEN_COOK_MODE),
                GeErdSensor(self, ErdCode.UPPER_OVEN_COOK_TIME_REMAINING),
                GeErdSensor(self, ErdCode.UPPER_OVEN_KITCHEN_TIMER),
                GeErdSensor(self, ErdCode.UPPER_OVEN_USER_TEMP_OFFSET),
                GeErdSensor(self, ErdCode.UPPER_OVEN_RAW_TEMPERATURE),
                GeErdBinarySensor(self, ErdCode.UPPER_OVEN_REMOTE_ENABLED),

                GeErdSensor(self, ErdCode.LOWER_OVEN_COOK_MODE),
                GeErdSensor(self, ErdCode.LOWER_OVEN_COOK_TIME_REMAINING),
                GeErdSensor(self, ErdCode.LOWER_OVEN_KITCHEN_TIMER),
                GeErdSensor(self, ErdCode.LOWER_OVEN_USER_TEMP_OFFSET),
                GeErdSensor(self, ErdCode.LOWER_OVEN_RAW_TEMPERATURE),
                GeErdBinarySensor(self, ErdCode.LOWER_OVEN_REMOTE_ENABLED),

                GeOven(self, LOWER_OVEN, True),
                GeOven(self, UPPER_OVEN, True),
            ])
        else:
            oven_entities.extend([
                GeErdSensor(self, ErdCode.UPPER_OVEN_COOK_MODE, self._single_name(ErdCode.UPPER_OVEN_COOK_MODE)),
                GeErdSensor(self, ErdCode.UPPER_OVEN_COOK_TIME_REMAINING, self._single_name(ErdCode.UPPER_OVEN_COOK_TIME_REMAINING)),
                GeErdSensor(self, ErdCode.UPPER_OVEN_KITCHEN_TIMER, self._single_name(ErdCode.UPPER_OVEN_KITCHEN_TIMER)),
                GeErdSensor(self, ErdCode.UPPER_OVEN_USER_TEMP_OFFSET, self._single_name(ErdCode.UPPER_OVEN_USER_TEMP_OFFSET)),
                GeErdSensor(self, ErdCode.UPPER_OVEN_RAW_TEMPERATURE, self._single_name(ErdCode.UPPER_OVEN_RAW_TEMPERATURE)),
                GeErdBinarySensor(self, ErdCode.UPPER_OVEN_REMOTE_ENABLED, self._single_name(ErdCode.UPPER_OVEN_REMOTE_ENABLED)),
                GeOven(self, UPPER_OVEN, False)
            ])

        if cooktop_config == ErdCooktopConfig.PRESENT:           
            cooktop_status: CooktopStatus = self.appliance.get_erd_value(ErdCode.COOKTOP_STATUS)
            cooktop_entities.append(GeErdBinarySensor(self, ErdCode.COOKTOP_STATUS))
            
            for (k, v) in cooktop_status.burners.items():
                if v.exists:
                    prop = self._camel_to_snake(k)
                    cooktop_entities.append(GeErdPropertyBinarySensor(self, ErdCode.COOKTOP_STATUS, prop+".on"))
                    cooktop_entities.append(GeErdPropertyBinarySensor(self, ErdCode.COOKTOP_STATUS, prop+".synchronized"))                    
                    if not v.on_off_only:
                        cooktop_entities.append(GeErdPropertySensor(self, ErdCode.COOKTOP_STATUS, prop+".power_pct", icon_override="mdi:fire", device_class_override=DEVICE_CLASS_POWER_FACTOR))

        return base_entities + oven_entities + cooktop_entities

    def _single_name(self, erd_code: ErdCode):
        return erd_code.name.replace(UPPER_OVEN+"_","").replace("_", " ").title()

    def _camel_to_snake(self, s):
        return ''.join(['_'+c.lower() if c.isupper() else c for c in s]).lstrip('_')    
