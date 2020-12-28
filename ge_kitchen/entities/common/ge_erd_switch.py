import logging

from homeassistant.components.switch import SwitchEntity
from .ge_erd_binary_sensor import GeErdBinarySensor

_LOGGER = logging.getLogger(__name__)

class GeErdSwitch(GeErdBinarySensor, SwitchEntity):
    """Switches for boolean ERD codes."""
    device_class = "switch"

    @property
    def is_on(self) -> bool:
        """Return True if switch is on."""
        return bool(self.appliance.get_erd_value(self.erd_code))

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.debug(f"Turning on {self.unique_id}")
        await self.appliance.async_set_erd_value(self.erd_code, True)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        _LOGGER.debug(f"Turning on {self.unique_id}")
        await self.appliance.async_set_erd_value(self.erd_code, False)

