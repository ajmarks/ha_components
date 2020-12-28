from typing import Optional

from homeassistant.components.binary_sensor import BinarySensorEntity

from .ge_erd_entity import GeErdEntity


class GeErdBinarySensor(GeErdEntity, BinarySensorEntity):
    """GE Entity for binary sensors"""
    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return bool(self.appliance.get_erd_value(self.erd_code))

    @property
    def icon(self) -> Optional[str]:
        return get_erd_icon(self.erd_code, self.is_on)

    @property
    def device_class(self) -> Optional[str]:
        if self.erd_code in DOOR_ERD_CODES:
            return "door"
        return None

