from typing import Optional

from gekitchen import ErdCodeType
from ge_kitchen.devices import ApplianceApi
from .ge_erd_binary_sensor import GeErdBinarySensor

class GeErdPropertyBinarySensor(GeErdBinarySensor):
    """GE Entity for property binary sensors"""
    def __init__(self, api: "ApplianceApi", erd_code: ErdCodeType, erd_property: str):
        super().__init__(api, erd_code)
        self.erd_property = erd_property

    @property
    def is_on(self) -> Optional[bool]:
        """Return True if entity is on."""
        try:
            value = getattr(self.appliance.get_erd_value(self.erd_code), self.erd_property)
        except KeyError:
            return None
        return boolify_erd_value(self.erd_code, value)

    @property
    def icon(self) -> Optional[str]:
        return get_erd_icon(self.erd_code, self.is_on)

    @property
    def unique_id(self) -> Optional[str]:
        return f"{super().unique_id}_{self.erd_property}"

    @property
    def name(self) -> Optional[str]:
        base_string = super().name
        property_name = self.erd_property.replace("_", " ").title()
        return f"{base_string} {property_name}"
