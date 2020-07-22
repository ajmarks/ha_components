"""Shark IQ Wrapper"""


import logging

from homeassistant.components.vacuum import (
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_ERROR,
    STATE_IDLE,
    STATE_PAUSED,
    STATE_RETURNING,
    SUPPORT_BATTERY,
    SUPPORT_FAN_SPEED,
    SUPPORT_LOCATE,
    SUPPORT_PAUSE,
    SUPPORT_RETURN_HOME,
    SUPPORT_START,
    SUPPORT_STATE,
    SUPPORT_STATUS,
    SUPPORT_STOP,
    StateVacuumEntity,
)
from sharkiqpy import SharkIqVacuum, PowerModes, OperatingModes, Properties
from typing import Dict, Optional
from .const import DOMAIN, SHARK

_LOGGER = logging.getLogger(__name__)

# Supported features
# TODO: Add support for mapping
SUPPORT_SHARKIQ = (
    SUPPORT_BATTERY
    | SUPPORT_FAN_SPEED
    | SUPPORT_PAUSE
    | SUPPORT_RETURN_HOME
    | SUPPORT_START
    | SUPPORT_STATE
    | SUPPORT_STATUS
    | SUPPORT_STOP
    | SUPPORT_LOCATE
)

OPERATING_STATE_MAP = {
    OperatingModes.PAUSE: STATE_PAUSED,
    OperatingModes.START: STATE_CLEANING,
    OperatingModes.STOP: STATE_IDLE,
    OperatingModes.RETURN: STATE_RETURNING,
}

FAN_SPEEDS_MAP = {
    "Eco": PowerModes.ECO,
    "Normal": PowerModes.NORMAL,
    "Max": PowerModes.MAX,
}

STATE_RECHARGING_TO_RESUME = 'recharging_to_resume'  # TODO: Add strings for this


class SharkVacuumEntity(StateVacuumEntity):
    """Shark IQ vacuum entity"""

    def __init__(self, sharkiq: SharkIqVacuum):
        self.sharkiq = sharkiq

    def clean_spot(self, **kwargs):
        raise NotImplementedError()

    def send_command(self, command, params=None, **kwargs):
        raise NotImplementedError()

    @property
    def name(self) -> str:
        return self.sharkiq.name

    @property
    def serial_number(self) -> str:
        """Device DSN"""
        return self.sharkiq.serial_number

    @property
    def model(self) -> str:
        if self.sharkiq.vac_model_number:
            return self.sharkiq.vac_model_number
        else:
            return self.sharkiq.oem_model_number

    @property
    def device_info(self) -> Dict:
        return {
            "identifiers": {
                (DOMAIN, self.serial_number)
            },
            "name": self.name,
            "manufacturer": SHARK,
            "model": self.model,
            "sw_version": self.sharkiq.get_property_value(Properties.ROBOT_FIRMWARE_VERSION)
        }

    @property
    def supported_features(self) -> int:
        """Flag vacuum cleaner robot features that are supported."""
        return SUPPORT_SHARKIQ

    @property
    def is_docked(self) -> Optional[bool]:
        """Is vacuum docked"""
        docked_status = self.sharkiq.get_property_value(Properties.DOCKED_STATUS)
        if docked_status is None:
            return None
        else:
            return docked_status == 1

    @property
    def error_code(self) -> Optional[int]:
        """Error code or None"""
        # Errors remain for a while, so we should only show an error if the device is stopped
        if self.sharkiq.get_property_value(Properties.OPERATING_MODE) == OperatingModes.STOP:
            return self.sharkiq.get_property_value(Properties.ERROR_CODE)
        else:
            return None

    @property
    def operating_mode(self) -> Optional[str]:
        """Operating mode"""
        op_mode = self.sharkiq.get_property_value(Properties.OPERATING_MODE)
        return OPERATING_STATE_MAP.get(op_mode)

    @property
    def recharging_to_resume(self) -> Optional[int]:
        return self.sharkiq.get_property_value(Properties.RECHARGING_TO_RESUME)

    @property
    def state(self):
        """Current state"""
        if self.recharging_to_resume:
            return STATE_RECHARGING_TO_RESUME
        elif self.is_docked:
            return STATE_DOCKED
        elif self.error_code:
            return STATE_ERROR
        else:
            return self.operating_mode

    @property
    def sharkiq_unique_id(self) -> str:
        """Return the uniqueid of the vacuum cleaner."""
        return "sharkiq-{:s}-vacuum".format(self.serial_number)

    @property
    def unique_id(self) -> str:
        """Return the unique id of the vacuum cleaner."""
        return self.sharkiq_unique_id

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True  # Always available, otherwise setup will fail

    @property
    def battery_level(self):
        """Current battery level"""
        return self.sharkiq.get_property_value(Properties.BATTERY_CAPACITY)

    def update(self, property_list=None):
        """Update the known properties"""
        self.sharkiq.update(property_list)

    async def async_update(self, property_list=None):
        """Update the known properties asynchronously"""
        await self.sharkiq.async_update(property_list)

    def return_to_base(self, **kwargs):
        """Have the device return to base"""
        self.sharkiq.set_operating_mode(OperatingModes.RETURN)

    def pause(self):
        """Pause the cleaning task."""
        self.sharkiq.set_operating_mode(OperatingModes.PAUSE)

    def start(self):
        """Start the device"""
        self.sharkiq.set_operating_mode(OperatingModes.START)

    def stop(self, **kwargs):
        """Stop the device"""
        self.sharkiq.set_operating_mode(OperatingModes.STOP)

    def locate(self, **kwargs):
        """Cause the device to generate a loud chirp"""
        self.sharkiq.find_device()

    async def async_return_to_base(self, **kwargs):
        """Have the device return to base"""
        await self.sharkiq.async_set_operating_mode(OperatingModes.RETURN)

    async def async_pause(self):
        """Pause the cleaning task."""
        await self.sharkiq.async_set_operating_mode(OperatingModes.PAUSE)

    async def async_start(self):
        """Start the device"""
        await self.sharkiq.async_set_operating_mode(OperatingModes.START)

    async def async_stop(self, **kwargs):
        """Stop the device"""
        await self.sharkiq.async_set_operating_mode(OperatingModes.STOP)

    async def async_locate(self, **kwargs):
        """Cause the device to generate a loud chirp"""
        await self.sharkiq.async_find_device()

    @property
    def fan_speed(self) -> str:
        """Return the current fan speed"""
        fan_speed = None
        speed_level = self.sharkiq.get_property_value(Properties.POWER_MODE)
        for k, val in FAN_SPEEDS_MAP.items():
            if val == speed_level:
                fan_speed = k
        return fan_speed

    def set_fan_speed(self, fan_speed: str, **kwargs):
        """Set the fan speed"""
        self.sharkiq.set_property_value(
            Properties.POWER_MODE, FAN_SPEEDS_MAP.get(fan_speed.capitalize())
        )

    @property
    def fan_speed_list(self):
        """Get the list of available fan speed steps of the vacuum cleaner."""
        return list(FAN_SPEEDS_MAP.keys())
