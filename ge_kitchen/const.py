"""Constants for the ge_kitchen integration."""
from gekitchensdk.const import LOGIN_URL

DOMAIN = "ge_kitchen"

EVENT_ALL_APPLIANCES_READY = 'all_appliances_ready'

UPDATE_INTERVAL = 30
ASYNC_TIMEOUT = 30
MIN_RETRY_DELAY = 15
MAX_RETRY_DELAY = 1800
RETRY_OFFLINE_COUNT = 5

