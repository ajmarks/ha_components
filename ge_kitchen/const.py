"""Constants for the ge_kitchen integration."""
from gekitchen.const import LOGIN_URL

DOMAIN = "ge_kitchen"

# TODO Update with your own urls
# OAUTH2_AUTHORIZE = f"{LOGIN_URL}/oauth2/auth"
OAUTH2_AUTH_URL = f"{LOGIN_URL}/oauth2/auth"
OAUTH2_TOKEN_URL = f"{LOGIN_URL}/oauth2/token"

AUTH_HANDLER = "auth_handler"
EVENT_ALL_APPLIANCES_READY = 'all_appliances_ready'
COORDINATOR = "coordinator"
GE_TOKEN = "ge_token"
MOBILE_DEVICE_TOKEN = "mdt"
XMPP_CREDENTIALS = "xmpp_credentials"

UPDATE_INTERVAL = 300
