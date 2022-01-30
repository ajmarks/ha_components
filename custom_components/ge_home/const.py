"""Constants for the gehome integration."""

DOMAIN = "ge_home"

EVENT_ALL_APPLIANCES_READY = 'all_appliances_ready'

UPDATE_INTERVAL = 30
ASYNC_TIMEOUT = 30
MIN_RETRY_DELAY = 15
MAX_RETRY_DELAY = 1800
RETRY_OFFLINE_COUNT = 5

SERVICE_SET_TIMER = "set_timer"
SERVICE_CLEAR_TIMER = "clear_timer"
SERVICE_SET_INT_VALUE = "set_int_value"

# Prevent Home Assistant automatic temperature conversions by overriding TEMP_CELCIUS, TEMP_FAHRENHEIT
# This makes sure that the values shows in the UI match device preferences bypassing the automatic conversion to whatever the Home Assistant default is set to
TEMP_CELSIUS = "\u2103"
TEMP_FAHRENHEIT = "\u2109"
