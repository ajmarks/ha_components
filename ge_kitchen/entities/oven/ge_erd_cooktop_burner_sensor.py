from typing import Optional
from ..common import GeErdPropertySensor

class GeErdCooktopBurnerSensor(GeErdPropertySensor):
    icon = "mdi:fire"
    
    @property
    def units(self) -> Optional[str]:
      return "%"

    @property
    def device_class(self) -> Optional[str]:
        return "power_factor"
