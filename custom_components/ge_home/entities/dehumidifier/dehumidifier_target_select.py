import logging
from typing import List, Any, Optional

from gehomesdk import ErdCodeType, DehumidifierTargetRange
from ...devices import ApplianceApi
from ..common import GeErdSelect, OptionsConverter

_LOGGER = logging.getLogger(__name__)

DEFAULT_MIN_HUMIDITY = 35
DEFAULT_MAX_HUMIDITY = 80

class DehumidifierTargetOptionsConverter(OptionsConverter):       
    def __init__(self, min = DEFAULT_MIN_HUMIDITY, max = DEFAULT_MAX_HUMIDITY) -> None:
        super().__init__()
        self._min = min
        self._max = max

    @property
    def options(self) -> List[str]:
        return [str(i) for i in range(min,max) if i % 5 == 0]
    
    def from_option_string(self, value: str) -> Any:
        return int(value)
    def to_option_string(self, value: int) -> Optional[str]:
        try:
            if value is not None:
                return str(value)
        except:
            return self._min

class DehumidifierTargetHumiditySelect(GeErdSelect):

    def __init__(self, api: ApplianceApi, erd_code: ErdCodeType, erd_override: str = None):
        self._low = DEFAULT_MIN_HUMIDITY
        self._high = DEFAULT_MAX_HUMIDITY

        #try to get the range
        value: DehumidifierTargetRange = api.try_get_erd_value(erd_code)
        if value is not None:
            self._low = value.min_humidity
            self._high = value.max_humidity

        super().__init__(api, erd_code, DehumidifierTargetOptionsConverter(self._low, self._high), erd_override=erd_override)
    
    @property
    def current_option(self):
        return self._converter.to_option_string(self.appliance.get_erd_value(self.erd_code))

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.debug(f"Setting select from {self.current_option} to {option}")
        
        new_state = self._converter.from_option_string(option)
        await self.appliance.async_set_erd_value(self.erd_code, new_state)
