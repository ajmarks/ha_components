import logging
from typing import List, Any, Optional

from gehomesdk import ErdAcFanSetting
from ..common import OptionsConverter

_LOGGER = logging.getLogger(__name__)

class DehumidifierFanSettingOptionsConverter(OptionsConverter):
    @property
    def options(self) -> List[str]:
        return [i.stringify() for i in [ErdAcFanSetting.DEFAULT, ErdAcFanSetting.LOW, ErdAcFanSetting.MED, ErdAcFanSetting.HIGH]]
 
    def from_option_string(self, value: str) -> Any:
        try:
            return ErdAcFanSetting[value.upper()]
        except:
            _LOGGER.warn(f"Could not set fan setting to {value.upper()}")
            return ErdAcFanSetting.DEFAULT
    def to_option_string(self, value: ErdAcFanSetting) -> Optional[str]:
        try:
            if value is not None:
                return value.stringify()
        except:
            pass
        return ErdAcFanSetting.DEFAULT.stringify()
