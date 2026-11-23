"""One coordinator per soundbar: one BLE connection per refresh, shared by all entities."""

import asyncio
from datetime import timedelta
import logging

from bleak import BleakError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .ble_connect import SoundbarNotFound, SoundbarTimeout, async_exchange
from .protocol import SoundbarState, parse_status

_LOGGER = logging.getLogger(__name__)

POLL_INTERVAL = timedelta(seconds=30)
RETRY_INTERVAL = timedelta(seconds=60)

EXCHANGE_ERRORS = (SoundbarNotFound, SoundbarTimeout, BleakError, ValueError)


class YamahaSoundbarCoordinator(DataUpdateCoordinator[SoundbarState]):
    """Reads the soundbar state and sends commands, one connection at a time."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._base_interval = POLL_INTERVAL if entry.data["polling_auto"] else None
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=entry.title,
            update_interval=self._base_interval,
            always_update=False,
        )
        self.address = entry.data["mac_adress"]
        self._lock = asyncio.Lock()

    async def _exchange(self, commands=()) -> SoundbarState:
        async with self._lock:
            return parse_status(await async_exchange(self.hass, self.address, commands))

    async def _async_update_data(self) -> SoundbarState:
        try:
            try:
                state = await self._exchange()
            except EXCHANGE_ERRORS as err:
                _LOGGER.debug("Status read failed (%s), trying once more", err)
                state = await self._exchange()
        except EXCHANGE_ERRORS as err:
            self.update_interval = RETRY_INTERVAL
            raise UpdateFailed(f"Soundbar {self.address} did not answer: {err}") from err
        self.update_interval = self._base_interval
        return state

    async def async_send_commands(self, commands) -> None:
        """Send commands in one connection, then share the state read back.

        `commands` can also be a function of the status frame read first (see async_exchange).
        """
        try:
            state = await self._exchange(commands)
        except EXCHANGE_ERRORS as err:
            # The commands may have reached the soundbar before the error: read the state again.
            await self.async_request_refresh()
            raise HomeAssistantError(f"Could not send command to the soundbar: {err}") from err
        self.update_interval = self._base_interval
        self.async_set_updated_data(state)
