from gehomesdk import ErdCode
from ...devices import ApplianceApi
from ..common import GeErdNumber
from ...const import TEMP_CELSIUS
from .ge_ccm_cached_value import GeCcmCachedValue

class GeCcmBrewTemperatureNumber(GeErdNumber, GeCcmCachedValue):
    def __init__(self, api: ApplianceApi):
        min_temp, max_temp, _ = api.appliance.get_erd_value(ErdCode.CCM_BREW_TEMPERATURE_RANGE)
        GeErdNumber.__init__(self, api = api, erd_code = ErdCode.CCM_BREW_TEMPERATURE, min_value=min_temp, max_value=max_temp, mode="slider")
        GeCcmCachedValue.__init__(self)

    async def async_set_value(self, value):
        GeCcmCachedValue.set_value(self, value)
        self.schedule_update_ha_state()

    @property
    def value(self):
        return int(self.get_value(device_value = super().value))

    @property
    def brew_temperature(self) -> int:

        value = self.value
        if self.unit_of_measurement == TEMP_CELSIUS:
            # Convert to Fahrenheit
            value = int(round(value * 9/5) + 32)
        
        return value