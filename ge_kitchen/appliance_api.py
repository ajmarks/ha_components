"""Oven state representation."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from gekitchen import ErdCodeType, GeAppliance, translate_erd_code
from gekitchen.erd_types import OvenCookSetting, OvenConfiguration
from gekitchen.erd_constants import (
    ErdCode,
    ErdApplianceType,
    ErdMeasurementUnits,
    ErdOvenState,
)
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .erd_string_utils import (
    oven_display_state_to_str,
    oven_cook_setting_to_str,
)

RAW_TEMPERATURE_ERD_CODES = {
    ErdCode.HOT_WATER_SET_TEMP,
    ErdCode.LOWER_OVEN_RAW_TEMPERATURE,
    ErdCode.LOWER_OVEN_USER_TEMP_OFFSET,
    ErdCode.UPPER_OVEN_RAW_TEMPERATURE,
    ErdCode.UPPER_OVEN_USER_TEMP_OFFSET,
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
        return f"GE Appliance {self.serial_number}"

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
            GeSensor(self, ErdCode.CLOCK_TIME),
            GeBinarySensor(self, ErdCode.SABBATH_MODE),
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
            GeSensor(self, ErdCode.UPPER_OVEN_COOK_MODE),
            GeSensor(self, ErdCode.UPPER_OVEN_COOK_TIME_REMAINING),
            GeSensor(self, ErdCode.UPPER_OVEN_CURRENT_STATE),
            GeSensor(self, ErdCode.UPPER_OVEN_DELAY_TIME_REMAINING),
            GeSensor(self, ErdCode.UPPER_OVEN_DISPLAY_TEMPERATURE),
            GeSensor(self, ErdCode.UPPER_OVEN_ELAPSED_COOK_TIME),
            GeSensor(self, ErdCode.UPPER_OVEN_KITCHEN_TIMER),
            GeSensor(self, ErdCode.UPPER_OVEN_PROBE_DISPLAY_TEMP),
            GeSensor(self, ErdCode.UPPER_OVEN_USER_TEMP_OFFSET),
            GeSensor(self, ErdCode.UPPER_OVEN_RAW_TEMPERATURE),
            GeBinarySensor(self, ErdCode.UPPER_OVEN_PROBE_PRESENT),
            GeBinarySensor(self, ErdCode.UPPER_OVEN_REMOTE_ENABLED),
        ]

        if oven_config.has_lower_oven:
            oven_entities.extend([
                GeSensor(self, ErdCode.LOWER_OVEN_COOK_MODE),
                GeSensor(self, ErdCode.LOWER_OVEN_COOK_TIME_REMAINING),
                GeSensor(self, ErdCode.LOWER_OVEN_CURRENT_STATE),
                GeSensor(self, ErdCode.LOWER_OVEN_DELAY_TIME_REMAINING),
                GeSensor(self, ErdCode.LOWER_OVEN_DISPLAY_TEMPERATURE),
                GeSensor(self, ErdCode.LOWER_OVEN_ELAPSED_COOK_TIME),
                GeSensor(self, ErdCode.LOWER_OVEN_KITCHEN_TIMER),
                GeSensor(self, ErdCode.LOWER_OVEN_PROBE_DISPLAY_TEMP),
                GeSensor(self, ErdCode.LOWER_OVEN_USER_TEMP_OFFSET),
                GeSensor(self, ErdCode.LOWER_OVEN_RAW_TEMPERATURE),
                GeBinarySensor(self, ErdCode.LOWER_OVEN_PROBE_PRESENT),
                GeBinarySensor(self, ErdCode.LOWER_OVEN_REMOTE_ENABLED),
            ])
        return base_entities + oven_entities


class GeEntity(Entity):
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


class GeSensor(GeErdEntity):
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


class GeBinarySensor(GeErdEntity):
    @property
    def is_on(self) -> bool:
        return bool(self.appliance.get_erd_value(self.erd_code))
