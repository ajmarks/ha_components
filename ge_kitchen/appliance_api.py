"""Oven state representation."""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Type

from gekitchen import ErdCodeType, GeAppliance, translate_erd_code
from gekitchen.erd_types import *
from gekitchen.erd_constants import *
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .erd_string_utils import *

RAW_TEMPERATURE_ERD_CODES = {
    ErdCode.HOT_WATER_SET_TEMP,
    ErdCode.LOWER_OVEN_RAW_TEMPERATURE,
    ErdCode.LOWER_OVEN_USER_TEMP_OFFSET,
    ErdCode.UPPER_OVEN_RAW_TEMPERATURE,
    ErdCode.UPPER_OVEN_USER_TEMP_OFFSET,
    ErdCode.CURRENT_TEMPERATURE,
    ErdCode.TEMPERATURE_SETTING,
}
NONZERO_TEMPERATURE_ERD_CODES = {
    ErdCode.LOWER_OVEN_DISPLAY_TEMPERATURE,
    ErdCode.LOWER_OVEN_PROBE_DISPLAY_TEMP,
    ErdCode.UPPER_OVEN_DISPLAY_TEMPERATURE,
    ErdCode.UPPER_OVEN_PROBE_DISPLAY_TEMP,
}
TEMPERATURE_ERD_CODES = RAW_TEMPERATURE_ERD_CODES.union(NONZERO_TEMPERATURE_ERD_CODES)
TIMER_ERD_CODES = {
    ErdCode.LOWER_OVEN_ELAPSED_COOK_TIME,
    ErdCode.LOWER_OVEN_KITCHEN_TIMER,
    ErdCode.LOWER_OVEN_DELAY_TIME_REMAINING,
    ErdCode.LOWER_OVEN_COOK_TIME_REMAINING,
    ErdCode.LOWER_OVEN_ELAPSED_COOK_TIME,
    ErdCode.ELAPSED_ON_TIME,
    ErdCode.TIME_REMAINING,
    ErdCode.UPPER_OVEN_ELAPSED_COOK_TIME,
    ErdCode.UPPER_OVEN_KITCHEN_TIMER,
    ErdCode.UPPER_OVEN_DELAY_TIME_REMAINING,
    ErdCode.UPPER_OVEN_ELAPSED_COOK_TIME,
    ErdCode.UPPER_OVEN_COOK_TIME_REMAINING,
}

_LOGGER = logging.getLogger(__name__)


def get_appliance_api_type(appliance_type: ErdApplianceType) -> Type:
    """Get the appropriate appliance type"""
    if appliance_type == ErdApplianceType.OVEN:
        return OvenApi
    if appliance_type == ErdApplianceType.FRIDGE:
        return FridgeApi
    # Fallback
    return ApplianceApi


def stringify_erd_value(erd_code: ErdCodeType, value: Any, units: str) -> Optional[str]:
    """
    Convert an erd property value to a nice string

    :param erd_code:
    :param value: The current value in its native format
    :param units: Units to apply, if applicable
    :return: The value converted to a string
    """
    erd_code = translate_erd_code(erd_code)

    if isinstance(value, ErdOvenState):
        return oven_display_state_to_str(value)
    if isinstance(value, OvenCookSetting):
        return oven_cook_setting_to_str(value, units)
    if isinstance(value, FridgeDoorStatus):
        return value.status
    if isinstance(value, FridgeIceBucketStatus):
        return bucket_status_to_str(value)
    if isinstance(value, ErdFilterStatus):
        return value.name.capitalize()
    if isinstance(value, HotWaterStatus):
        return hot_water_status_str(value)

    if erd_code == ErdCode.CLOCK_TIME:
        return value.strftime('%H:%M:%S') if value else None
    if erd_code in RAW_TEMPERATURE_ERD_CODES:
        return f"{value}{units}"
    if erd_code in NONZERO_TEMPERATURE_ERD_CODES:
        return f"{value}{units}" if value else ''
    if erd_code in TIMER_ERD_CODES:
        return str(value)[:-3] if value else ''
    if value is None:
        return None
    return str(value)


def get_erd_units(erd_code: ErdCodeType, measurement_units: ErdMeasurementUnits):
    erd_code = translate_erd_code(erd_code)
    if not measurement_units:
        return None

    if erd_code in TEMPERATURE_ERD_CODES or erd_code in {ErdCode.LOWER_OVEN_COOK_MODE, ErdCode.UPPER_OVEN_COOK_MODE}:
        if measurement_units == ErdMeasurementUnits.METRIC:
            return TEMP_CELSIUS
        return TEMP_FAHRENHEIT
    return None


def get_erd_icon(erd_code: ErdCodeType) -> Optional[str]:
    erd_code = translate_erd_code(erd_code)
    if not isinstance(erd_code, ErdCode):
        return None
    if erd_code in TIMER_ERD_CODES:
        return 'mdi:timer-outline'
    if erd_code in {
        ErdCode.LOWER_OVEN_COOK_MODE,
        ErdCode.LOWER_OVEN_CURRENT_STATE,
        ErdCode.LOWER_OVEN_WARMING_DRAWER_STATE,
        ErdCode.UPPER_OVEN_COOK_MODE,
        ErdCode.UPPER_OVEN_CURRENT_STATE,
        ErdCode.UPPER_OVEN_WARMING_DRAWER_STATE,
        ErdCode.WARMING_DRAWER_STATE,
    }:
        return 'mdi:stove'
    if erd_code in {
        ErdCode.TURBO_COOL_STATUS,
        ErdCode.TURBO_FREEZE_STATUS,
    }:
        return 'mdi:snowflake'
    if erd_code == ErdCode.SABBATH_MODE:
        return 'mdi:judaism'

    return None


class ApplianceApi:
    """
    API class to represent a single physical device.

    Since a physical device can have many entities, we'll pool common elements here
    """
    APPLIANCE_TYPE = None  # type: Optional[ErdApplianceType]

    def __init__(self, hass: HomeAssistant, appliance: GeAppliance):
        if not appliance.initialized:
            raise RuntimeError('Appliance not ready')
        self._appliance = appliance
        self._loop = appliance.client.loop
        self._hass = hass
        self.initial_update = False
        self._entities = {}  # type: Optional[Dict[str, Entity]]

    @property
    def hass(self) -> HomeAssistant:
        return self._hass

    @property
    def loop(self) -> Optional[asyncio.AbstractEventLoop]:
        if self._loop is None:
            self._loop = self._appliance.client.loop
        return self._loop

    @property
    def appliance(self) -> GeAppliance:
        return self._appliance

    @property
    def serial_number(self) -> str:
        return self.appliance.get_erd_value(ErdCode.SERIAL_NUMBER)

    @property
    def model_number(self) -> str:
        return self.appliance.get_erd_value(ErdCode.MODEL_NUMBER)

    @property
    def name(self) -> str:
        appliance_type = self.appliance.appliance_type
        if appliance_type is None or appliance_type == ErdApplianceType.UNKNOWN:
            appliance_type = "Appliance"
        else:
            appliance_type = appliance_type.name.replace("_", " ").title()
        return f"GE {appliance_type} {self.serial_number}"

    @property
    def device_info(self) -> Dict:
        """Device info dictionary."""
        return {
            "identifiers": {(DOMAIN, self.serial_number)},
            "name": self.name,
            "manufacturer": "GE",
            "model": self.model_number
        }

    @property
    def entities(self) -> List[Entity]:
        return list(self._entities.values())

    def get_all_entities(self) -> List[Entity]:
        """Create Entities for this device."""
        entities = [
            GeErdSensor(self, ErdCode.CLOCK_TIME),
            GeErdSwitch(self, ErdCode.SABBATH_MODE),
        ]
        return entities

    def build_entities_list(self) -> None:
        """Build the entities list, adding anything new."""
        entities = [
            e for e in self.get_all_entities()
            if not isinstance(e, GeErdEntity) or e.erd_code in self.appliance.known_properties
        ]

        for entity in entities:
            if entity.unique_id not in self._entities:
                self._entities[entity.unique_id] = entity


class OvenApi(ApplianceApi):
    """API class for oven objects"""
    APPLIANCE_TYPE = ErdApplianceType.OVEN

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()
        oven_config = self.appliance.get_erd_value(ErdCode.OVEN_CONFIGURATION)  # type: OvenConfiguration
        _LOGGER.debug(f'Oven Config: {oven_config}')
        oven_entities = [
            GeErdSensor(self, ErdCode.UPPER_OVEN_COOK_MODE),
            GeErdSensor(self, ErdCode.UPPER_OVEN_COOK_TIME_REMAINING),
            GeErdSensor(self, ErdCode.UPPER_OVEN_CURRENT_STATE),
            GeErdSensor(self, ErdCode.UPPER_OVEN_DELAY_TIME_REMAINING),
            GeErdSensor(self, ErdCode.UPPER_OVEN_DISPLAY_TEMPERATURE),
            GeErdSensor(self, ErdCode.UPPER_OVEN_ELAPSED_COOK_TIME),
            GeErdSensor(self, ErdCode.UPPER_OVEN_KITCHEN_TIMER),
            GeErdSensor(self, ErdCode.UPPER_OVEN_PROBE_DISPLAY_TEMP),
            GeErdSensor(self, ErdCode.UPPER_OVEN_USER_TEMP_OFFSET),
            GeErdSensor(self, ErdCode.UPPER_OVEN_RAW_TEMPERATURE),
            GeBinarySensor(self, ErdCode.UPPER_OVEN_PROBE_PRESENT),
            GeBinarySensor(self, ErdCode.UPPER_OVEN_REMOTE_ENABLED),
        ]

        if oven_config.has_lower_oven:
            oven_entities.extend([
                GeErdSensor(self, ErdCode.LOWER_OVEN_COOK_MODE),
                GeErdSensor(self, ErdCode.LOWER_OVEN_COOK_TIME_REMAINING),
                GeErdSensor(self, ErdCode.LOWER_OVEN_CURRENT_STATE),
                GeErdSensor(self, ErdCode.LOWER_OVEN_DELAY_TIME_REMAINING),
                GeErdSensor(self, ErdCode.LOWER_OVEN_DISPLAY_TEMPERATURE),
                GeErdSensor(self, ErdCode.LOWER_OVEN_ELAPSED_COOK_TIME),
                GeErdSensor(self, ErdCode.LOWER_OVEN_KITCHEN_TIMER),
                GeErdSensor(self, ErdCode.LOWER_OVEN_PROBE_DISPLAY_TEMP),
                GeErdSensor(self, ErdCode.LOWER_OVEN_USER_TEMP_OFFSET),
                GeErdSensor(self, ErdCode.LOWER_OVEN_RAW_TEMPERATURE),
                GeBinarySensor(self, ErdCode.LOWER_OVEN_PROBE_PRESENT),
                GeBinarySensor(self, ErdCode.LOWER_OVEN_REMOTE_ENABLED),
            ])
        return base_entities + oven_entities


class FridgeApi(ApplianceApi):
    """API class for oven objects"""
    APPLIANCE_TYPE = ErdApplianceType.FRIDGE

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()

        fridge_entities = [
            # GeErdSensor(self, ErdCode.AIR_FILTER_STATUS),
            GeErdSensor(self, ErdCode.DOOR_STATUS),
            GeErdSensor(self, ErdCode.FRIDGE_MODEL_INFO),
            # GeErdSensor(self, ErdCode.HOT_WATER_LOCAL_USE),
            # GeErdSensor(self, ErdCode.HOT_WATER_SET_TEMP),
            # GeErdSensor(self, ErdCode.HOT_WATER_STATUS),
            GeErdSensor(self, ErdCode.ICE_MAKER_BUCKET_STATUS),
            # GeErdSensor(self, ErdCode.ICE_MAKER_CONTROL),
            # GeErdSensor(self, ErdCode.SETPOINT_LIMITS),
            GeErdPropertySensor(self, ErdCode.TEMPERATURE_SETTING, 'fridge'),
            GeErdPropertySensor(self, ErdCode.TEMPERATURE_SETTING, 'freezer'),
            GeErdPropertySensor(self, ErdCode.CURRENT_TEMPERATURE, 'fridge'),
            GeErdPropertySensor(self, ErdCode.CURRENT_TEMPERATURE, 'freezer'),
            GeErdSwitch(self, ErdCode.TURBO_COOL_STATUS),
            GeErdSwitch(self, ErdCode.TURBO_FREEZE_STATUS),
            GeErdSensor(self, ErdCode.WATER_FILTER_STATUS),
        ]
        return base_entities + fridge_entities


class GeEntity:
    """Base class for all GE Entities"""
    def __init__(self, api: ApplianceApi):
        self._api = api
        self.hass = None  # type: Optional[HomeAssistant]

    @property
    def unique_id(self) -> str:
        raise NotImplementedError

    @property
    def api(self) -> ApplianceApi:
        return self._api

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self.api.device_info

    @property
    def serial_number(self):
        return self.api.serial_number

    @property
    def should_poll(self) -> bool:
        """Don't poll."""
        return False

    @property
    def available(self) -> bool:
        return self.appliance.available

    @property
    def appliance(self) -> GeAppliance:
        return self.api.appliance

    @property
    def name(self) -> Optional[str]:
        raise NotImplementedError


class GeErdEntity(GeEntity):
    """Parent class for GE entities tied to a specific ERD"""
    def __init__(self, api: ApplianceApi, erd_code: ErdCodeType):
        super().__init__(api)
        self._erd_code = translate_erd_code(erd_code)

    @property
    def erd_code(self) -> ErdCodeType:
        return self._erd_code

    @property
    def erd_string(self) -> str:
        erd_code = self.erd_code
        if isinstance(self.erd_code, ErdCode):
            return erd_code.name
        return erd_code

    @property
    def name(self) -> Optional[str]:
        erd_string = self.erd_string
        return ' '.join(erd_string.split('_')).title()

    @property
    def unique_id(self) -> Optional[str]:
        return f'{DOMAIN}_{self.serial_number}_{self.erd_string.lower()}'

    @property
    def icon(self) -> Optional[str]:
        return get_erd_icon(self.erd_code)


class GeErdSensor(GeErdEntity, Entity):
    """GE Entity for sensors"""
    @property
    def state(self) -> Optional[str]:
        try:
            value = self.appliance.get_erd_value(self.erd_code)
        except KeyError:
            return None
        return stringify_erd_value(self.erd_code, value, self.units)

    @property
    def measurement_system(self) -> Optional[ErdMeasurementUnits]:
        return self.appliance.get_erd_value(ErdCode.TEMPERATURE_UNIT)

    @property
    def units(self) -> Optional[str]:
        return get_erd_units(self.erd_code, self.measurement_system)

    @property
    def device_class(self) -> Optional[str]:
        if self.erd_code in TEMPERATURE_ERD_CODES:
            return 'temperature'
        return None


class GeErdPropertySensor(GeErdSensor):
    """GE Entity for sensors"""
    def __init__(self, api: ApplianceApi, erd_code: ErdCodeType, erd_property: str):
        super().__init__(api, erd_code)
        self.erd_property = erd_property

    @property
    def unique_id(self) -> Optional[str]:
        return f"{super().unique_id}_{self.erd_property}"

    @property
    def name(self) -> Optional[str]:
        base_string = super().name
        property_name = self.erd_property.replace("_", " ").title()
        return f"{base_string} {property_name}"

    @property
    def state(self) -> Optional[str]:
        try:
            value = getattr(self.appliance.get_erd_value(self.erd_code), self.erd_property)
        except KeyError:
            return None
        return stringify_erd_value(self.erd_code, value, self.units)

    @property
    def measurement_system(self) -> Optional[ErdMeasurementUnits]:
        return self.appliance.get_erd_value(ErdCode.TEMPERATURE_UNIT)

    @property
    def units(self) -> Optional[str]:
        return get_erd_units(self.erd_code, self.measurement_system)

    @property
    def device_class(self) -> Optional[str]:
        if self.erd_code in TEMPERATURE_ERD_CODES:
            return 'temperature'
        return None


class GeBinarySensor(GeErdEntity, BinarySensorEntity):
    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return bool(self.appliance.get_erd_value(self.erd_code))


class GeErdSwitch(GeBinarySensor, SwitchEntity):
    """Switches for boolean ERD codes."""
    device_class = "switch"

    @property
    def is_on(self) -> bool:
        """Return True if switch is on."""
        return bool(self.appliance.get_erd_value(self.erd_code))

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self.appliance.async_set_erd_value(self.erd_code, True)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self.appliance.async_set_erd_value(self.erd_code, False)
