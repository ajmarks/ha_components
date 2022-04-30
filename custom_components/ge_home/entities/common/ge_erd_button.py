from typing import Optional

from homeassistant.components.button import ButtonEntity

from gehomesdk import ErdCodeType
from ...devices import ApplianceApi
from .ge_erd_entity import GeErdEntity


class GeErdButton(GeErdEntity, ButtonEntity):
    def __init__(self, api: ApplianceApi, erd_code: ErdCodeType, erd_override: str = None):
        super().__init__(api, erd_code, erd_override=erd_override)

    """GE Entity for buttons"""
    async def async_press(self) -> None:
        """Handle the button press."""
        await self.appliance.async_set_erd_value(self.erd_code, True)
