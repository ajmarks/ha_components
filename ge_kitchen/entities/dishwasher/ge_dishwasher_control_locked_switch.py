from gekitchen import ErdCode, ErdOperatingMode

from ..common import GeErdSwitch

class GeDishwasherControlLockedSwitch(GeErdSwitch):
    @property
    def is_on(self) -> bool:
        mode: ErdOperatingMode = self.appliance.get_erd_value(ErdCode.OPERATING_MODE)
        return mode == ErdOperatingMode.CONTROL_LOCKED
    