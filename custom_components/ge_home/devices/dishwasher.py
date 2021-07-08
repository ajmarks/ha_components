import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gehomesdk.erd import ErdCode, ErdApplianceType

from .base import ApplianceApi
from ..entities import GeErdSensor, GeErdBinarySensor, GeErdPropertySensor

_LOGGER = logging.getLogger(__name__)


class DishwasherApi(ApplianceApi):
    """API class for dishwasher objects"""
    APPLIANCE_TYPE = ErdApplianceType.DISH_WASHER

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
            GeErdBinarySensor(self, ErdCode.DISHWASHER_DOOR_STATUS),

            #User Setttings
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "sound", icon_override="mdi:volume-high"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "lock_control", icon_override="mdi:lock"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "sabbath", icon_override="mdi:star-david"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "cycle_mode"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "presoak"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "bottle_jet"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "wash_temp", icon_override="mdi:coolant-temperature"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "dry_option"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "wash_zone"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "delay_hours", icon_override="mdi:clock-fast")
        ]
        entities = base_entities + dishwasher_entities
        return entities
        
