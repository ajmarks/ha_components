"""Oven state representation."""

import asyncio
import logging
from typing import Dict, List, Optional, Type, TYPE_CHECKING

from gekitchen import GeAppliance
from gekitchen.erd_constants import *
from gekitchen.erd_types import *

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .binary_sensor import GeErdBinarySensor
from .const import DOMAIN
from .entities import GeErdEntity
from .sensor import GeErdSensor
from .switch import GeErdSwitch
from .water_heater import (
    GeFreezerEntity,
    GeFridgeEntity,
    GeOvenHeaterEntity,
    LOWER_OVEN,
    UPPER_OVEN,
)




_LOGGER = logging.getLogger(__name__)


def get_appliance_api_type(appliance_type: ErdApplianceType) -> Type:
    """Get the appropriate appliance type"""
    if appliance_type == ErdApplianceType.OVEN:
        return OvenApi
    if appliance_type == ErdApplianceType.FRIDGE:
        return FridgeApi
    # Fallback
    return ApplianceApi


class ApplianceApi:
    """
    API class to represent a single physical device.

    Since a physical device can have many entities, we"ll pool common elements here
    """
    APPLIANCE_TYPE = None  # type: Optional[ErdApplianceType]

    def __init__(self, coordinator: DataUpdateCoordinator, appliance: GeAppliance):
        if not appliance.initialized:
            raise RuntimeError("Appliance not ready")
        self._appliance = appliance
        self._loop = appliance.client.loop
        self._hass = coordinator.hass
        self.coordinator = coordinator
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
            "model": self.model_number,
            "sw_version": self.appliance.get_erd_value(ErdCode.WIFI_MODULE_SW_VERSION),
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
        oven_config: OvenConfiguration = self.appliance.get_erd_value(ErdCode.OVEN_CONFIGURATION)
        _LOGGER.debug(f"Oven Config: {oven_config}")
        oven_entities = [
            GeErdSensor(self, ErdCode.UPPER_OVEN_COOK_MODE),
            GeErdSensor(self, ErdCode.UPPER_OVEN_COOK_TIME_REMAINING),
            GeErdSensor(self, ErdCode.UPPER_OVEN_KITCHEN_TIMER),
            GeErdSensor(self, ErdCode.UPPER_OVEN_USER_TEMP_OFFSET),
            GeErdBinarySensor(self, ErdCode.UPPER_OVEN_REMOTE_ENABLED),
        ]

        if oven_config.has_lower_oven:
            oven_entities.extend([
                GeErdSensor(self, ErdCode.LOWER_OVEN_COOK_MODE),
                GeErdSensor(self, ErdCode.LOWER_OVEN_COOK_TIME_REMAINING),
                GeErdSensor(self, ErdCode.LOWER_OVEN_USER_TEMP_OFFSET),
                GeErdBinarySensor(self, ErdCode.LOWER_OVEN_REMOTE_ENABLED),
                GeOvenHeaterEntity(self, LOWER_OVEN, True),
                GeOvenHeaterEntity(self, UPPER_OVEN, True),
            ])
        else:
            oven_entities.append(GeOvenHeaterEntity(self, UPPER_OVEN, False))
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
            GeErdSwitch(self, ErdCode.SABBATH_MODE),
            GeFreezerEntity(self),
            GeFridgeEntity(self),
        ]
        entities = base_entities + fridge_entities
        return entities
