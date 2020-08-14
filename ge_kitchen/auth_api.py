"""API for ge_kitchen bound to Home Assistant OAuth."""

import gekitchen
import time
from aiohttp import ClientSession
from gekitchen.const import (
    API_URL,
    LOGIN_URL,
    OAUTH2_APP_ID,
    OAUTH2_CLIENT_ID,
    OAUTH2_CLIENT_SECRET,
)
from homeassistant.helpers import config_entry_oauth2_flow
from typing import Dict, Optional
from .const import GE_TOKEN, MOBILE_DEVICE_TOKEN, XMPP_CREDENTIALS


class AsyncConfigEntryAuth(gekitchen.AbstractAuth):
    """Provide ge_kitchen authentication tied to an OAuth2 based config entry."""

    def __init__(
        self,
        websession: ClientSession,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
    ):
        """Initialize ge_kitchen auth."""
        super().__init__(websession)
        self._oauth_session = oauth_session

    async def async_get_access_token(self):
        """Return a valid access token."""
        await self._oauth_session.async_ensure_token_valid()

        return self._oauth_session.token

    @property
    def mdt(self) -> Optional[str]:
        return self._oauth_session.config_entry.data.get(MOBILE_DEVICE_TOKEN)

    @property
    def ge_token(self) -> Optional[Dict]:
        return self._oauth_session.config_entry.data.get(GE_TOKEN)

    async def async_get_mdt(self) -> str:
        """Get a mobile device token."""

        mdt = self.mdt
        if mdt:
            return mdt

        mdt_data = {
            'kind': 'mdt#login',
            'app': OAUTH2_APP_ID,
            'os': 'google_android'
        }
        async with self.request('post', f'{API_URL}/v1/mdt', json=mdt_data) as r:
            results = await r.json()

        try:
            mdt = results['mdt']
        except KeyError:
            raise RuntimeError(f'Failed to get a mobile device token: {results}')

        self._oauth_session.hass.config_entries.async_update_entry(
            self._oauth_session.config_entry, data={**self._oauth_session.config_entry.data, MOBILE_DEVICE_TOKEN: mdt}
        )
        return mdt

    async def get_new_ge_token(self) -> Dict:
        mdt = await self.async_get_mdt()

        params = {
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
            'mdt': mdt
        }
        async with self.request('post', f'{LOGIN_URL}/oauth2/getoken', params=params) as r:
            ge_token = await r.json()

        if 'access_token' not in ge_token['access_token']:
            raise RuntimeError(f'Failed to get a GE token: {ge_token}')

        ge_token['expires_at'] = time.time() + ge_token['expires_in']
        self._oauth_session.hass.config_entries.async_update_entry(
            self._oauth_session.config_entry, data={**self._oauth_session.config_entry.data, GE_TOKEN: ge_token}
        )
        return ge_token

    @property
    def ge_token_valid(self) -> bool:
        try:
            return self.ge_token['expires_at'] > time.time() + 10
        except KeyError:
            return False

    async def async_ensure_ge_token_valid(self):
        if not self.ge_token_valid:
            await self.get_new_ge_token()

    async def async_get_xmpp_credentials(self) -> Dict:
        await self.async_ensure_ge_token_valid()

        ge_token = self.ge_token
        session = self.websession

        uri = f'{API_URL}/v1/mdt/credentials'
        headers = {"Authorization": f"Bearer {ge_token['access_token']:s}"}
        async with session.get(uri, headers=headers) as r:
            xmpp_credentials = await r.json()

        self._oauth_session.hass.config_entries.async_update_entry(
            self._oauth_session.config_entry,
            data={**self._oauth_session.config_entry.data, XMPP_CREDENTIALS: xmpp_credentials}
        )
        return xmpp_credentials
