from gehomesdk import ErdCode
from ...devices import ApplianceApi
from ..common import GeErdButton

class GeCcmBrewSettingsButton(GeErdButton):
    def __init__(self, api: ApplianceApi):
        super().__init__(api, erd_code=ErdCode.CCM_BREW_SETTINGS)

    async def async_press(self) -> None:
        """Handle the button press."""

        # Forward the call up to the Coffee Maker device to handle
        await self.api.start_brewing()