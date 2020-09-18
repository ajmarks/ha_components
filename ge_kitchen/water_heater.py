"""GE Kitchen Sensor Entities"""
import abc
import async_timeout
from datetime import timedelta
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from bidict import bidict
from gekitchen import (
    ErdCode,
    ErdDoorStatus,
    ErdFilterStatus,
    ErdFullNotFull,
    ErdHotWaterStatus,
    ErdMeasurementUnits,
    ErdOnOff,
    ErdOvenCookMode,
    ErdPodStatus,
    ErdPresent,
    OVEN_COOK_MODE_MAP,
)
from gekitchen.erd_types import (
    FridgeDoorStatus,
    FridgeSetPointLimits,
    FridgeSetPoints,
    FridgeIceBucketStatus,
    HotWaterStatus,
    IceMakerControlStatus,
    OvenCookMode,
    OvenCookSetting,
)

from homeassistant.components.water_heater import (
    SUPPORT_OPERATION_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    WaterHeaterEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.core import HomeAssistant

from .entities import GeEntity, stringify_erd_value
from .const import DOMAIN

if TYPE_CHECKING:
    from .appliance_api import ApplianceApi
    from .update_coordinator import GeKitchenUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

ATTR_DOOR_STATUS = "door_status"
GE_FRIDGE_SUPPORT = (SUPPORT_OPERATION_MODE | SUPPORT_TARGET_TEMPERATURE)
HEATER_TYPE_FRIDGE = "fridge"
HEATER_TYPE_FREEZER = "freezer"

# Fridge/Freezer
OP_MODE_K_CUP = "K-Cup Brewing"
OP_MODE_NORMAL = "Normal"
OP_MODE_SABBATH = "Sabbath Mode"
OP_MODE_TURBO_COOL = "Turbo Cool"
OP_MODE_TURBO_FREEZE = "Turbo Freeze"

# Oven
OP_MODE_OFF = "Off"
OP_MODE_BAKE = "Bake"
OP_MODE_CONVMULTIBAKE = "Conv. Multi-Bake"
OP_MODE_CONVBAKE = "Convection Bake"
OP_MODE_CONVROAST = "Convection Roast"
OP_MODE_COOK_UNK = "Unknown"

UPPER_OVEN = "UPPER_OVEN"
LOWER_OVEN = "LOWER_OVEN"

COOK_MODE_OP_MAP = bidict({
    ErdOvenCookMode.NOMODE: OP_MODE_OFF,
    ErdOvenCookMode.CONVMULTIBAKE_NOOPTION: OP_MODE_CONVMULTIBAKE,
    ErdOvenCookMode.CONVBAKE_NOOPTION: OP_MODE_CONVBAKE,
    ErdOvenCookMode.CONVROAST_NOOPTION: OP_MODE_CONVROAST,
    ErdOvenCookMode.BAKE_NOOPTION: OP_MODE_BAKE,
})


class GeAbstractFridgeEntity(GeEntity, WaterHeaterEntity, metaclass=abc.ABCMeta):
    """Mock a fridge or freezer as a water heater."""

    @property
    def heater_type(self) -> str:
        raise NotImplementedError

    @property
    def turbo_erd_code(self) -> str:
        raise NotImplementedError

    @property
    def turbo_mode(self) -> str:
        raise NotImplementedError

    @property
    def operation_list(self) -> List[str]:
        return [OP_MODE_NORMAL, OP_MODE_SABBATH, self.turbo_mode]

    @property
    def unique_id(self) -> str:
        return f"{self.serial_number}-{self.heater_type}"

    @property
    def name(self) -> Optional[str]:
        return f"GE {self.heater_type.title()} {self.serial_number}"

    @property
    def temperature_unit(self):
        measurement_system = self.appliance.get_erd_value(ErdCode.TEMPERATURE_UNIT)
        if measurement_system == ErdMeasurementUnits.METRIC:
            return TEMP_CELSIUS
        return TEMP_FAHRENHEIT

    @property
    def target_temps(self) -> FridgeSetPoints:
        """Get the current temperature settings tuple."""
        return self.appliance.get_erd_value(ErdCode.TEMPERATURE_SETTING)

    @property
    def target_temperature(self) -> int:
        """Return the temperature we try to reach."""
        return getattr(self.target_temps, self.heater_type)

    @property
    def current_temperature(self) -> int:
        """Return the current temperature."""
        current_temps = self.appliance.get_erd_value(ErdCode.CURRENT_TEMPERATURE)
        current_temp = getattr(current_temps, self.heater_type)
        if current_temp is None:
            _LOGGER.exception(f"{self.name} has None for current_temperature (available: {self.available})!")
        return current_temp

    async def async_set_temperature(self, **kwargs):
        target_temp = kwargs.get(ATTR_TEMPERATURE)
        if target_temp is None:
            return
        if not self.min_temp <= target_temp <= self.max_temp:
            raise ValueError("Tried to set temperature out of device range")

        if self.heater_type == HEATER_TYPE_FRIDGE:
            new_temp = FridgeSetPoints(fridge=target_temp, freezer=self.target_temps.freezer)
        elif self.heater_type == HEATER_TYPE_FREEZER:
            new_temp = FridgeSetPoints(fridge=self.target_temps.fridge, freezer=target_temp)
        else:
            raise ValueError("Invalid heater_type")

        await self.appliance.async_set_erd_value(ErdCode.TEMPERATURE_SETTING, new_temp)

    @property
    def supported_features(self):
        return GE_FRIDGE_SUPPORT

    @property
    def setpoint_limits(self) -> FridgeSetPointLimits:
        return self.appliance.get_erd_value(ErdCode.SETPOINT_LIMITS)

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return getattr(self.setpoint_limits, f"{self.heater_type}_min")

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return getattr(self.setpoint_limits, f"{self.heater_type}_max")

    @property
    def current_operation(self) -> str:
        """Get ther current operation mode."""
        if self.appliance.get_erd_value(ErdCode.SABBATH_MODE):
            return OP_MODE_SABBATH
        if self.appliance.get_erd_value(self.turbo_erd_code):
            return self.turbo_mode
        return OP_MODE_NORMAL

    async def async_set_sabbath_mode(self, sabbath_on: bool = True):
        """Set sabbath mode if it's changed"""
        if self.appliance.get_erd_value(ErdCode.SABBATH_MODE) == sabbath_on:
            return
        await self.appliance.async_set_erd_value(ErdCode.SABBATH_MODE, sabbath_on)

    async def async_set_operation_mode(self, operation_mode):
        """Set the operation mode."""
        if operation_mode not in self.operation_list:
            raise ValueError("Invalid operation mode")
        if operation_mode == self.current_operation:
            return
        sabbath_mode = operation_mode == OP_MODE_SABBATH
        await self.async_set_sabbath_mode(sabbath_mode)
        if not sabbath_mode:
            await self.appliance.async_set_erd_value(self.turbo_erd_code, operation_mode == self.turbo_mode)

    @property
    def door_status(self) -> FridgeDoorStatus:
        """Shorthand to get door status."""
        return self.appliance.get_erd_value(ErdCode.DOOR_STATUS)

    @property
    def ice_maker_state_attrs(self) -> Dict[str, Any]:
        """Get state attributes for the ice maker, if applicable."""
        data = {}

        erd_val: FridgeIceBucketStatus = self.appliance.get_erd_value(ErdCode.ICE_MAKER_BUCKET_STATUS)
        ice_bucket_status = getattr(erd_val, f"state_full_{self.heater_type}")
        if ice_bucket_status != ErdFullNotFull.NA:
            data["ice_bucket"] = ice_bucket_status.name.replace("_", " ").title()

        erd_val: IceMakerControlStatus = self.appliance.get_erd_value(ErdCode.ICE_MAKER_CONTROL)
        ice_control_status = getattr(erd_val, f"status_{self.heater_type}")
        if ice_control_status != ErdOnOff.NA:
            data["ice_maker"] = ice_control_status.name.replace("_", " ").lower()

        return data

    @property
    def door_state_attrs(self) -> Dict[str, Any]:
        """Get state attributes for the doors."""
        return {}

    @property
    def other_state_attrs(self) -> Dict[str, Any]:
        """State attributes to be optionally overridden in subclasses."""
        return {}

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        door_attrs = self.door_state_attrs
        ice_maker_attrs = self.ice_maker_state_attrs
        other_attrs = self.other_state_attrs
        return {**door_attrs, **ice_maker_attrs, **other_attrs}


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


class GeFridgeWaterHeater(GeEntity, WaterHeaterEntity):
    """Entity for in-fridge water heaters"""

    # These values are from FridgeHotWaterFragment.smali in the android app
    min_temp = 90
    max_temp = 185

    @property
    def hot_water_status(self) -> HotWaterStatus:
        """Access the main status value conveniently."""
        return self.appliance.get_erd_value(ErdCode.HOT_WATER_STATUS)

    @property
    def unique_id(self) -> str:
        """Make a unique id."""
        return f"{self.serial_number}-fridge-hot-water"

    @property
    def name(self) -> Optional[str]:
        """Name it reasonably."""
        return f"GE Fridge Water Heater {self.serial_number}"

    @property
    def temperature_unit(self):
        """Select the appropriate temperature unit."""
        measurement_system = self.appliance.get_erd_value(ErdCode.TEMPERATURE_UNIT)
        if measurement_system == ErdMeasurementUnits.METRIC:
            return TEMP_CELSIUS
        return TEMP_FAHRENHEIT

    @property
    def supports_k_cups(self) -> bool:
        """Return True if the device supports k-cup brewing."""
        status = self.hot_water_status
        return status.pod_status != ErdPodStatus.NA and status.brew_module != ErdPresent.NA

    @property
    def operation_list(self) -> List[str]:
        """Supported Operations List"""
        ops_list = [OP_MODE_NORMAL, OP_MODE_SABBATH]
        if self.supports_k_cups:
            ops_list.append(OP_MODE_K_CUP)
        return ops_list

    async def async_set_temperature(self, **kwargs):
        pass

    async def async_set_operation_mode(self, operation_mode):
        pass

    @property
    def supported_features(self):
        pass

    @property
    def current_operation(self) -> str:
        """Get the current operation mode."""
        if self.appliance.get_erd_value(ErdCode.SABBATH_MODE):
            return OP_MODE_SABBATH
        return OP_MODE_NORMAL

    @property
    def current_temperature(self) -> Optional[int]:
        """Return the current temperature."""
        return self.hot_water_status.current_temp


class GeOvenHeaterEntity(GeEntity, WaterHeaterEntity):
    """Water Heater entity for ovens"""

    icon = "mdi:stove"

    def __init__(self, api: "ApplianceApi", oven_select: str = UPPER_OVEN, two_cavity: bool = False):
        if oven_select not in (UPPER_OVEN, LOWER_OVEN):
            raise ValueError(f"Invalid `oven_select` value ({oven_select})")

        self._oven_select = oven_select
        self._two_cavity = two_cavity
        super().__init__(api)

    @property
    def supported_features(self):
        return GE_FRIDGE_SUPPORT

    @property
    def unique_id(self) -> str:
        return f"{self.serial_number}-{self.oven_select.lower()}"

    @property
    def name(self) -> Optional[str]:
        if self._two_cavity:
            oven_title = self.oven_select.replace("_", " ").title()
        else:
            oven_title = "Oven"

        return f"GE {oven_title}"

    @property
    def temperature_unit(self):
        measurement_system = self.appliance.get_erd_value(ErdCode.TEMPERATURE_UNIT)
        if measurement_system == ErdMeasurementUnits.METRIC:
            return TEMP_CELSIUS
        return TEMP_FAHRENHEIT

    @property
    def oven_select(self) -> str:
        return self._oven_select

    def get_erd_code(self, suffix: str) -> ErdCode:
        """Return the appropriate ERD code for this oven_select"""
        return ErdCode[f"{self.oven_select}_{suffix}"]

    @property
    def current_temperature(self) -> Optional[int]:
        current_temp = self.get_erd_value("DISPLAY_TEMPERATURE")
        if current_temp:
            return current_temp
        return self.get_erd_value("RAW_TEMPERATURE")

    @property
    def current_operation(self) -> Optional[str]:
        cook_setting = self.current_cook_setting
        cook_mode = cook_setting.cook_mode
        # TODO: simplify this lookup nonsense somehow
        current_state = OVEN_COOK_MODE_MAP.inverse[cook_mode]
        try:
            return COOK_MODE_OP_MAP[current_state]
        except KeyError:
            _LOGGER.debug(f"Unable to map {current_state} to an operation mode")
            return OP_MODE_COOK_UNK

    @property
    def operation_list(self) -> List[str]:
        erd_code = self.get_erd_code("AVAILABLE_COOK_MODES")
        cook_modes: Set[ErdOvenCookMode] = self.appliance.get_erd_value(erd_code)
        op_modes = [o for o in (COOK_MODE_OP_MAP[c] for c in cook_modes) if o]
        op_modes = [OP_MODE_OFF] + op_modes
        return op_modes

    @property
    def current_cook_setting(self) -> OvenCookSetting:
        """Get the current cook mode."""
        erd_code = self.get_erd_code("COOK_MODE")
        return self.appliance.get_erd_value(erd_code)

    @property
    def target_temperature(self) -> Optional[int]:
        """Return the temperature we try to reach."""
        cook_mode = self.current_cook_setting
        if cook_mode.temperature:
            return cook_mode.temperature
        return None

    @property
    def min_temp(self) -> int:
        """Return the minimum temperature."""
        min_temp, _ = self.appliance.get_erd_value(ErdCode.OVEN_MODE_MIN_MAX_TEMP)
        return min_temp

    @property
    def max_temp(self) -> int:
        """Return the maximum temperature."""
        _, max_temp = self.appliance.get_erd_value(ErdCode.OVEN_MODE_MIN_MAX_TEMP)
        return max_temp

    async def async_set_operation_mode(self, operation_mode: str):
        """Set the operation mode."""

        erd_cook_mode = COOK_MODE_OP_MAP.inverse[operation_mode]
        # Pick a temperature to set.  If there's not one already set, default to
        # good old 350F.
        if operation_mode == OP_MODE_OFF:
            target_temp = 0
        elif self.target_temperature:
            target_temp = self.target_temperature
        elif self.temperature_unit == TEMP_FAHRENHEIT:
            target_temp = 350
        else:
            target_temp = 177

        new_cook_mode = OvenCookSetting(OVEN_COOK_MODE_MAP[erd_cook_mode], target_temp)
        erd_code = self.get_erd_code("COOK_MODE")
        await self.appliance.async_set_erd_value(erd_code, new_cook_mode)

    async def async_set_temperature(self, **kwargs):
        """Set the cook temperature"""
        target_temp = kwargs.get(ATTR_TEMPERATURE)
        if target_temp is None:
            return

        current_op = self.current_operation
        if current_op != OP_MODE_OFF:
            erd_cook_mode = COOK_MODE_OP_MAP.inverse[current_op]
        else:
            erd_cook_mode = ErdOvenCookMode.BAKE_NOOPTION

        new_cook_mode = OvenCookSetting(OVEN_COOK_MODE_MAP[erd_cook_mode], target_temp)
        erd_code = self.get_erd_code("COOK_MODE")
        await self.appliance.async_set_erd_value(erd_code, new_cook_mode)

    def get_erd_value(self, suffix: str) -> Any:
        erd_code = self.get_erd_code(suffix)
        return self.appliance.get_erd_value(erd_code)

    @property
    def display_state(self) -> Optional[str]:
        erd_code = self.get_erd_code("CURRENT_STATE")
        erd_value = self.appliance.get_erd_value(erd_code)
        return stringify_erd_value(erd_code, erd_value, self.temperature_unit)

    @property
    def device_state_attributes(self) -> Optional[Dict[str, Any]]:
        probe_present = self.get_erd_value("PROBE_PRESENT")
        data = {
            "display_state": self.display_state,
            "probe_present": probe_present,
            "raw_temperature": self.get_erd_value("RAW_TEMPERATURE"),
        }
        if probe_present:
            data["probe_temperature"] = self.get_erd_value("PROBE_DISPLAY_TEMP")
        elapsed_time = self.get_erd_value("ELAPSED_COOK_TIME")
        cook_time_left = self.get_erd_value("COOK_TIME_REMAINING")
        kitchen_timer = self.get_erd_value("KITCHEN_TIMER")
        delay_time = self.get_erd_value("DELAY_TIME_REMAINING")
        if elapsed_time:
            data["cook_time_elapsed"] = str(elapsed_time)
        if cook_time_left:
            data["cook_time_left"] = str(cook_time_left)
        if kitchen_timer:
            data["cook_time_remaining"] = str(kitchen_timer)
        if delay_time:
            data["delay_time_remaining"] = str(delay_time)
        return data


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable):
    """GE Kitchen sensors."""
    _LOGGER.debug('Adding GE "Water Heaters"')
    coordinator: "GeKitchenUpdateCoordinator" = hass.data[DOMAIN][config_entry.entry_id]

    # This should be a NOP, but let's be safe
    with async_timeout.timeout(20):
        await coordinator.initialization_future
    _LOGGER.debug('Coordinator init future finished')

    apis = list(coordinator.appliance_apis.values())
    _LOGGER.debug(f'Found {len(apis):d} appliance APIs')
    entities = [
        entity for api in apis for entity in api.entities
        if isinstance(entity, WaterHeaterEntity)
    ]
    _LOGGER.debug(f'Found {len(entities):d} "water heaters"')
    async_add_entities(entities)
