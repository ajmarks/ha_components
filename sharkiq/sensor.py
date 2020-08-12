"""Sensor for checking the battery level of Shark IQ"""
import logging

from homeassistant.const import DEVICE_CLASS_BATTERY, UNIT_PERCENTAGE
from homeassistant.helpers.icon import icon_for_battery_level
from typing import Callable, List, TYPE_CHECKING

from sharkiqpy import Properties
from .const import DOMAIN, SHARKIQ_SESSION
from .sharkiq import SharkVacuumEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from sharkiqpy import AylaApi, SharkIqVacuum

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: "HomeAssistant", config_entry, async_add_entities: Callable):
    """Set up the Shark IQ battery sensor"""
    domain_data = hass.data[DOMAIN][config_entry.entry_id]
    ayla_api = domain_data[SHARKIQ_SESSION]  # type: AylaApi

    devices = await ayla_api.async_get_devices()  # type: List[SharkIqVacuum]
    device_names = ', '.join([d.name for d in devices])
    _LOGGER.debug("Found % Shark IQ device(s): %s", len(devices), device_names)
    async_add_entities([SharkIqBattery(d) for d in devices], True)


class SharkIqBattery(SharkVacuumEntity):
    """Class to hold Shark IQ battery info"""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.sharkiq.name} Battery Level"

    @property
    def unique_id(self) -> str:
        """Return the unique id of the vacuum cleaner."""
        return "sharkiq-{:s}-battery".format(self.serial_number)

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS_BATTERY

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return UNIT_PERCENTAGE

    @property
    def icon(self):
        """Return the icon for the battery."""
        charging = self.sharkiq.get_property_value(Properties.CHARGING_STATUS)

        return icon_for_battery_level(battery_level=self.battery_level, charging=charging)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.battery_level
