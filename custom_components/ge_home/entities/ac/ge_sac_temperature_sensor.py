import logging
from typing import Any, List, Optional

from homeassistant.const import (
    TEMP_FAHRENHEIT
)
from ..common import GeErdSensor

class GeSacTemperatureSensor(GeErdSensor):
    """Class for Split A/C temperature sensors"""

    @property
    def temperature_unit(self):
        #SAC appears to be hard coded to use Fahrenheit internally, no matter what the display shows
        return TEMP_FAHRENHEIT
