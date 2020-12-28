"""GE Kitchen Sensor Entities - Freezer"""
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from gekitchen import (
    ErdCode,
    ErdDoorStatus
)

from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT
from ..entities import GeEntity
from .abstract_fridge_entity import (
    ATTR_DOOR_STATUS, 
    HEATER_TYPE_FREEZER, 
    OP_MODE_TURBO_FREEZE,
    GeAbstractFridgeEntity
)

_LOGGER = logging.getLogger(__name__)

class GeFreezerEntity(GeAbstractFridgeEntity):
    """A freezer is basically a fridge."""

    heater_type = HEATER_TYPE_FREEZER
    turbo_erd_code = ErdCode.TURBO_FREEZE_STATUS
    turbo_mode = OP_MODE_TURBO_FREEZE
    icon = "mdi:fridge-top"

    @property
    def door_state_attrs(self) -> Optional[Dict[str, Any]]:
        door_status = self.door_status.freezer
        if door_status and door_status != ErdDoorStatus.NA:
            return {ATTR_DOOR_STATUS: door_status.name.title()}
        return {}

