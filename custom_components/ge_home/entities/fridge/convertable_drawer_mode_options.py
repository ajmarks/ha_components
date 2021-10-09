import logging
from typing import List, Any, Optional

from gehomesdk import ErdConvertableDrawerMode
from ..common import OptionsConverter

_LOGGER = logging.getLogger(__name__)

class ConvertableDrawerModeOptionsConverter(OptionsConverter):
    def __init__(self):
        super().__init__()
        self._excluded_options = [
            ErdConvertableDrawerMode.UNKNOWN0, 
            ErdConvertableDrawerMode.UNKNOWN1,
            ErdConvertableDrawerMode.NA
        ]

    @property
    def options(self) -> List[str]:
        return [i.stringify() for i in ErdConvertableDrawerMode if i not in self._excluded_options]
    def from_option_string(self, value: str) -> Any:
        try:
            return ErdConvertableDrawerMode[value.upper()]
        except:
            _LOGGER.warn(f"Could not set hood light level to {value.upper()}")
            return ErdConvertableDrawerMode.NA
    def to_option_string(self, value: ErdConvertableDrawerMode) -> Optional[str]:
        try:
            if value is not None:
                return value.stringify()
        except:
            pass
        return ErdConvertableDrawerMode.NA.stringify()

