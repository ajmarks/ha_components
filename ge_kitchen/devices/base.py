import asyncio
import logging
from typing import Dict, List, Optional

from gekitchensdk import GeAppliance
from gekitchensdk.erd import ErdCode, ErdApplianceType

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ..entities import GeErdEntity, GeErdSensor, GeErdSwitch
from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

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
