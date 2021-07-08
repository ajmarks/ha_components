from homeassistant.components.ge_home.entities.common.ge_erd_select import GeErdSelect
from homeassistant.components.ge_home.entities.common.ge_erd_entity import GeErdEntity
from homeassistant.components.ge_home.devices.base import ApplianceApi
import logging
from typing import Optional, Dict, Any

from gehomesdk import ErdCode, ErdCodeClass, ErdCodeType
from gehomesdk.erd.values.waterfilter.erd_waterfilter_position import (
    ErdWaterFilterPosition,
)

from ...const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ErdFilterPositionSelect(GeErdEntity, GeErdSelect):
    def __init__(
        self,
        api: ApplianceApi,
        erd_code: ErdCodeType,
    ):
        super().__init__(api=api, erd_code=erd_code)
        self._attr_hass = api._hass
        self.hass = api._hass
        self._attr_unique_id = self.unique_id
        self._attr_name = self.name
        self._attr_current_option = ErdWaterFilterPosition.UNKNOWN.name
        self._attr_icon = self.icon
        self._attr_device_class = self.device_class
        self._attr_options = [
            ErdWaterFilterPosition.BYPASS.name,
            ErdWaterFilterPosition.OFF.name,
            ErdWaterFilterPosition.FILTERED.name,
            ErdWaterFilterPosition.READY.name,
        ]
        self._attr_device_info = self.device_info

    async def async_select_option(self, option: str) -> None:
        if (
            option == ErdWaterFilterPosition.READY.name
            or option == ErdWaterFilterPosition.UNKNOWN.name
        ):
            return
        await self.api.appliance.async_set_erd_value(
            self.erd_code, ErdWaterFilterPosition[option]
        )

    @property
    def icon(self) -> str:
        return "mdi:water"
