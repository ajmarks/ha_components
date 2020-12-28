from typing import Optional

from gekitchen import ErdCode, ErdCodeType, ErdCodeClass

from ge_kitchen.const import DOMAIN
from ge_kitchen.devices import ApplianceApi
from .ge_entity import GeEntity


class GeErdEntity(GeEntity):
    """Parent class for GE entities tied to a specific ERD"""
    def __init__(self, api: ApplianceApi, erd_code: ErdCodeType, erd_override: str = None):
        super().__init__(api)
        self._erd_code = api.appliance.translate_erd_code(erd_code)
        self._erd_code_class = api.appliance.get_erd_code_class(self._erd_code)
        self._erd_override = erd_override
        
    @property
    def erd_code(self) -> ErdCodeType:
        return self._erd_code
    
    @property
    def erd_code_class(self) -> ErdCodeClass:
        return self._erd_code_class

    @property
    def erd_string(self) -> str:
        erd_code = self.erd_code
        if isinstance(self.erd_code, ErdCode):
            return erd_code.name
        return erd_code

    @property
    def name(self) -> Optional[str]:
        erd_string = self.erd_string
        
        #override the name if specified
        if self._erd_override != None:
            erd_string = self._erd_override

        erd_title = " ".join(erd_string.split("_")).title()
        return f"{self.serial_number} {erd_title}"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{DOMAIN}_{self.serial_number}_{self.erd_string.lower()}"

    @property
    def icon(self) -> Optional[str]:
        return get_erd_icon(self.erd_code)

    def _stringify_erd_value(self, value: any, **kwargs) -> Optional[str]:
        # perform special processing before passing over to the default method
        if self.erd_code == ErdCode.CLOCK_TIME:
            return value.strftime("%H:%M:%S") if value else None        
        if self.erd_code_class == ErdCodeClass.RAW_TEMPERATURE:
            return f"{value}"
        if self.erd_code_class == ErdCodeClass.NON_ZERO_TEMPERATURE:
            return f"{value}" if value else ""
        if self.erd_code_class == ErdCodeClass.TIMER:
            return str(value)[:-3] if value else ""
        if value is None:
            return None
        return self.appliance.stringify_erd_value(self.erd_code, value, kwargs)

    def _boolify_erd_value(self, value: any) -> Optional[bool]:
        return self.appliance.boolify_erd_value(self.erd_code, value)
