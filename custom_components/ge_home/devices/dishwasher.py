from custom_components.ge_home.entities.common.ge_erd_binary_sensor import GeErdBinarySensor
from custom_components.ge_home.entities.common.ge_erd_property_binary_sensor import GeErdPropertyBinarySensor
import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gehomesdk.erd import ErdCode, ErdApplianceType

from .base import ApplianceApi
from ..entities import GeErdSensor, GeErdPropertySensor, GeDishwasherControlLockedSwitch

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
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "sound"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "lock_control"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "sabbath"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "cycle_mode"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "presoak"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "bottle_jet"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "wash_temp"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "dry_option"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "wash_zone"),
            GeErdPropertySensor(self, ErdCode.DISHWASHER_USER_SETTING, "delay_hours")
        ]
        entities = base_entities + dishwasher_entities
        return entities
        
