from datetime import timedelta
from typing import Optional, Dict, Any

from gekitchen import GeAppliance
from ge_kitchen.devices import ApplianceApi

class GeEntity:
    """Base class for all GE Entities"""
    should_poll = False

    def __init__(self, api: ApplianceApi):
        self._api = api
        self.hass = None

    @property
    def unique_id(self) -> str:
        raise NotImplementedError

    @property
    def api(self) -> ApplianceApi:
        return self._api

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self.api.device_info

    @property
    def serial_number(self):
        return self.api.serial_number

    @property
    def available(self) -> bool:
        return self.appliance.available

    @property
    def appliance(self) -> GeAppliance:
        return self.api.appliance

    @property
    def name(self) -> Optional[str]:
        raise NotImplementedError

    def _stringify(self, value: any, **kwargs) -> Optional[str]:
        if isinstance(timedelta):
            return str(value)[:-3] if value else ""
        if value is None:
            return None
        return self.appliance.stringify_erd_value(value, kwargs)

    def _boolify(self, value: any) -> Optional[bool]:
        return self.appliance.boolify_erd_value(value)
