import logging

from homeassistant.components.select import SelectEntity

_LOGGER = logging.getLogger(__name__)


class GeErdSelect(SelectEntity):
    """Switches for boolean ERD codes."""

    device_class = "select"
