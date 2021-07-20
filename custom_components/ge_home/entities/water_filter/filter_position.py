import logging
from typing import List, Any, Optional

from gehomesdk import ErdCodeType, ErdWaterFilterPosition
from ...devices import ApplianceApi
from ..common import GeErdSelect, OptionsConverter

_LOGGER = logging.getLogger(__name__)

class FilterPositionOptionsConverter(OptionsConverter):
    @property
    def options(self) -> List[str]:
        return [i.name.title() for i in ErdWaterFilterPosition if i != ErdWaterFilterPosition.UNKNOWN]
    def from_option_string(self, value: str) -> Any:
        try:
            return ErdWaterFilterPosition[value.upper()]
        except:
            _LOGGER.warn(f"Could not set filter position to {value.upper()}")
            return ErdWaterFilterPosition.UNKNOWN
    def to_option_string(self, value: Any) -> Optional[str]:
        try:
            if value is not None:
                return value.name.title()
        except:
            pass
        return ErdWaterFilterPosition.UNKNOWN.name.title()

class GeErdFilterPositionSelect(GeErdSelect):
    def __init__(self, api: ApplianceApi, erd_code: ErdCodeType):
        super().__init__(api, erd_code, FilterPositionOptionsConverter())

    async def async_select_option(self, option: str) -> None:
        value = self._converter.from_option_string(option)
        if value in [ErdWaterFilterPosition.UNKNOWN, ErdWaterFilterPosition.READY]:
            return
        return await super().async_select_option(option)
