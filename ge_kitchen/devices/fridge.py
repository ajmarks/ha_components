from homeassistant.components.binary_sensor import DEVICE_CLASS_PROBLEM
from homeassistant.const import DEVICE_CLASS_TEMPERATURE
import logging
from typing import List

from homeassistant.helpers.entity import Entity
from gekitchensdk import (
    ErdCode, 
    ErdApplianceType,
    ErdOnOff,
    ErdHotWaterStatus,
    FridgeIceBucketStatus,
    IceMakerControlStatus,
    ErdFilterStatus,
    HotWaterStatus,
    FridgeModelInfo
)

from .base import ApplianceApi
from ..entities import (
    GeErdSensor, 
    GeErdSwitch, 
    GeFridge, 
    GeFreezer, 
    GeDispenser, 
    GeErdPropertySensor,
    GeErdPropertyBinarySensor
)

_LOGGER = logging.getLogger(__name__)

class FridgeApi(ApplianceApi):
    """API class for oven objects"""
    APPLIANCE_TYPE = ErdApplianceType.FRIDGE

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()
    
        fridge_entities = []
        freezer_entities = []
        dispenser_entities = []

        # Get the statuses used to determine presence
        ice_maker_control: IceMakerControlStatus = self.appliance.get_erd_value(ErdCode.ICE_MAKER_CONTROL)
        ice_bucket_status: FridgeIceBucketStatus = self.appliance.get_erd_value(ErdCode.ICE_MAKER_BUCKET_STATUS)
        water_filter: ErdFilterStatus = self.appliance.get_erd_value(ErdCode.WATER_FILTER_STATUS)
        air_filter: ErdFilterStatus = self.appliance.get_erd_value(ErdCode.AIR_FILTER_STATUS)
        hot_water_status: HotWaterStatus = self.appliance.get_erd_value(ErdCode.HOT_WATER_STATUS)
        fridge_model_info: FridgeModelInfo = self.appliance.get_erd_value(ErdCode.FRIDGE_MODEL_INFO)

        # Common entities
        common_entities = [
            GeErdSensor(self, ErdCode.FRIDGE_MODEL_INFO),
            GeErdSwitch(self, ErdCode.SABBATH_MODE),
            GeErdSensor(self, ErdCode.DOOR_STATUS),
            GeErdPropertyBinarySensor(self, ErdCode.DOOR_STATUS, "any_open")
        ]
        if(ice_bucket_status and (ice_bucket_status.is_present_fridge or ice_bucket_status.is_present_freezer)):
            common_entities.append(GeErdSensor(self, ErdCode.ICE_MAKER_BUCKET_STATUS))

        # Fridge entities
        if fridge_model_info.has_fridge:
            fridge_entities.extend([
                GeErdPropertySensor(self, ErdCode.CURRENT_TEMPERATURE, "fridge"),
                GeFridge(self),
            ])
            if(ice_maker_control and ice_maker_control.status_fridge != ErdOnOff.NA):
                fridge_entities.append(GeErdPropertyBinarySensor(self, ErdCode.ICE_MAKER_CONTROL, "status_fridge"))
            if(water_filter and water_filter != ErdFilterStatus.NA):
                fridge_entities.append(GeErdSensor(self, ErdCode.WATER_FILTER_STATUS))
            if(air_filter and air_filter != ErdFilterStatus.NA):
                fridge_entities.append(GeErdSensor(self, ErdCode.AIR_FILTER_STATUS))    
            if(ice_bucket_status and ice_bucket_status.is_present_fridge):
                GeErdPropertySensor(self, ErdCode.ICE_MAKER_BUCKET_STATUS, "state_full_fridge")

        # Freezer entities
        if fridge_model_info.has_freezer:
            freezer_entities.extend([
                GeErdPropertySensor(self, ErdCode.CURRENT_TEMPERATURE, "freezer"),
                GeFreezer(self),                  
            ])
            if(ice_maker_control and ice_maker_control.status_freezer != ErdOnOff.NA):
                GeErdPropertyBinarySensor(self, ErdCode.ICE_MAKER_CONTROL, "status_freezer")
            if(ice_bucket_status and ice_bucket_status.is_present_freezer):
                GeErdPropertySensor(self, ErdCode.ICE_MAKER_BUCKET_STATUS, "state_full_freezer")

        # Dispenser entities
        if(hot_water_status and hot_water_status.status != ErdHotWaterStatus.NA):
            dispenser_entities.extend([
                GeErdSensor(self, ErdCode.HOT_WATER_IN_USE),
                GeErdSensor(self, ErdCode.HOT_WATER_SET_TEMP),
                GeErdPropertySensor(self, ErdCode.HOT_WATER_STATUS, "status"),
                GeErdPropertySensor(self, ErdCode.HOT_WATER_STATUS, "time_remaining", icon_override="mdi:timer-outline"),
                GeErdPropertySensor(self, ErdCode.HOT_WATER_STATUS, "current_temp", device_class_override=DEVICE_CLASS_TEMPERATURE),
                GeErdPropertyBinarySensor(self, ErdCode.HOT_WATER_STATUS, "faulted", device_class_override=DEVICE_CLASS_PROBLEM),
                GeDispenser(self)
            ])

        entities = base_entities + common_entities + fridge_entities + freezer_entities + dispenser_entities
        return entities
