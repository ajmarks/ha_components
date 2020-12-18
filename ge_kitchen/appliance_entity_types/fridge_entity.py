"""GE Kitchen Sensor Entities - Fridge"""
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from gekitchen import (
    ErdCode,
    ErdDoorStatus,
    ErdFilterStatus
)

from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT
from ..entities import GeEntity
from .abstract_fridge_entity import (
    ATTR_DOOR_STATUS,
    HEATER_TYPE_FRIDGE, 
    OP_MODE_TURBO_COOL,
    GeAbstractFridgeEntity
)

_LOGGER = logging.getLogger(__name__)

class GeFridgeEntity(GeAbstractFridgeEntity):
    heater_type = HEATER_TYPE_FRIDGE
    turbo_erd_code = ErdCode.TURBO_COOL_STATUS
    turbo_mode = OP_MODE_TURBO_COOL
    icon = "mdi:fridge-bottom"

    @property
    def available(self) -> bool:
        available = super().available
        if not available:
            app = self.appliance
            _LOGGER.critical(f"{self.name} unavailable. Appliance info: Availaible - {app._available} and Init - {app.initialized}")
        return available

    @property
    def other_state_attrs(self) -> Dict[str, Any]:
        """Water filter state."""
        filter_status: ErdFilterStatus = self.appliance.get_erd_value(ErdCode.WATER_FILTER_STATUS)
        if filter_status == ErdFilterStatus.NA:
            return {}
        return {"water_filter_status": filter_status.name.replace("_", " ").title()}

    @property
    def door_state_attrs(self) -> Dict[str, Any]:
        """Get state attributes for the doors."""
        data = {}
        door_status = self.door_status
        if not door_status:
            return {}
        door_right = door_status.fridge_right
        door_left = door_status.fridge_left
        drawer = door_status.drawer

        if door_right and door_right != ErdDoorStatus.NA:
            data["right_door"] = door_status.fridge_right.name.title()
        if door_left and door_left != ErdDoorStatus.NA:
            data["left_door"] = door_status.fridge_left.name.title()
        if drawer and drawer != ErdDoorStatus.NA:
            data["drawer"] = door_status.fridge_left.name.title()

        if data:
            all_closed = all(v == "Closed" for v in data.values())
            data[ATTR_DOOR_STATUS] = "Closed" if all_closed else "Open"

        return data
