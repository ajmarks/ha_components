import logging
from typing import List, Any, NamedTuple, Optional

from gehomesdk import ErdCcmBrewStrength, ErdCcmBrewSettings
from homeassistant.const import TEMP_FAHRENHEIT
from homeassistant.util.unit_system import UnitSystem

from custom_components.ge_home.entities.ccm.const import MAX_CUPS, MIN_CUPS
from ..common import OptionsConverter

_LOGGER = logging.getLogger(__name__)

class CcmBrewOption(NamedTuple):
    strength: ErdCcmBrewStrength
    cups: int

    def stringify(self):
        return f"{self.strength.stringify()} -- {self.cups} cups"

class CcmBrewOptionsConverter(OptionsConverter):
    def __init__(self, units: UnitSystem):
        super().__init__()
        self._units = units
        self._options = self._build_options()

    @property
    def options(self) -> List[str]:
        options = ["Off"]
        options.extend([i.stringify() for i in self._options])
        options.extend(["Descale"])

        return options

    def from_option_string(self, value: str) -> Optional[ErdCcmBrewSettings]:
        try:
            if value in ["Off","Descale"]:
                return None
            s = value.split(" -- ")[0].upper()
            c = value.split(" -- ")[1].replace(" cups","")
            return ErdCcmBrewSettings(int(c), ErdCcmBrewStrength[s], 200)
        except:
            _LOGGER.error(f"Could not convert brew options '{value}'", exc_info=True)

            #return a default if we can't interpret it
            return ErdCcmBrewSettings(4, ErdCcmBrewStrength.MEDIUM, 200)    

    def to_option_string(self, value: ErdCcmBrewSettings) -> Optional[str]:
        try:
            o = CcmBrewOption(value.brew_strength, value.number_of_cups)
            return o.stringify()
        except:
            #return a default if we can't interpret it
            return CcmBrewOption(ErdCcmBrewStrength.MEDIUM, 4)

    def _build_options(self) -> List[CcmBrewOption]:
        options = []
        for s in filter(lambda x: x != ErdCcmBrewStrength.UNKNOWN, ErdCcmBrewStrength):
            for c in range(MIN_CUPS, MAX_CUPS, 2):
                options.append(CcmBrewOption(s, c))

        return options
