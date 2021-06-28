from gehomesdk import ErdCode, ErdOperatingMode
from gehomesdk.erd.values.common.erd_measurement_units import ErdMeasurementUnits
from typing import Optional

from ..common import GeErdSensor


class ErdFlowRateSensor(GeErdSensor):
    @property
    def state(self) -> Optional[float]:
        try:
            value = self.appliance.get_erd_value(self.erd_code)
        except KeyError:
            return None
        return value.flow_rate

    @property
    def unit_of_measurement(self) -> Optional[str]:
        if self._temp_measurement_system == ErdMeasurementUnits.METRIC:
            return "lpm"
        return "gpm"
