from gehomesdk import ErdCode, ErdOperatingMode
from gehomesdk.erd.values.common.erd_measurement_units import ErdMeasurementUnits
from typing import Optional

from ..common import GeErdSensor


class ErdFilterLifeRemainingSensor(GeErdSensor):
    @property
    def state(self) -> Optional[int]:
        try:
            value = self.appliance.get_erd_value(self.erd_code)
        except KeyError:
            return None
        return value.life_remaining

    @property
    def unit_of_measurement(self) -> Optional[str]:
        return "%"
