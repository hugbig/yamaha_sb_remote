import asyncio
from bleak import BleakClient
from bleak_retry_connector import establish_connection
import logging
from homeassistant.components import bluetooth
from .protocol import is_status_frame
from .utils import create_command_code, interpret_message

_LOGGER = logging.getLogger(__name__)


NOTIFY_UUID = "5cafe9de-e7b0-4e0b-8fb9-2da91a7ae3ed"
WRITE_UUID = "0c50e7fa-594c-408b-ae0d-b53b884b7c08"
STATUS_TIMEOUT = 5.0


class SoundbarNotFound(Exception):
    """No Bluetooth adapter or proxy can see the soundbar."""


class SoundbarTimeout(Exception):
    """The soundbar did not send its status in time."""


async def _wait_status(statuses: asyncio.Queue) -> bytes:
    try:
        async with asyncio.timeout(STATUS_TIMEOUT):
            return await statuses.get()
    except TimeoutError as err:
        raise SoundbarTimeout("No status notification from the soundbar") from err


async def async_exchange(hass, address: str, commands=()) -> bytes:
    """Connect once: read the status, send the commands, read the status again.

    `commands` is a list of commands, or a function that gets the first status frame and returns
    them (so they can depend on the current state). Return the last status frame. The caller
    makes sure only one exchange runs at a time.
    """
    device = bluetooth.async_ble_device_from_address(hass, address, connectable=True)
    if device is None:
        raise SoundbarNotFound(f"Bluetooth device {address} not found")

    statuses: asyncio.Queue[bytes] = asyncio.Queue()

    def on_notify(_characteristic, data: bytearray) -> None:
        frame = bytes(data)
        if is_status_frame(frame):
            statuses.put_nowait(frame)
        elif len(frame) > 3:
            _LOGGER.debug("Event from soundbar: %s", interpret_message(frame))

    request = create_command_code(["request"])
    client = None
    try:
        client = await establish_connection(BleakClient, device, address)
        await client.start_notify(NOTIFY_UUID, on_notify)
        await client.write_gatt_char(WRITE_UUID, request)
        frame = await _wait_status(statuses)
        if callable(commands):
            commands = commands(frame)
        if commands:
            for command in commands:
                await client.write_gatt_char(WRITE_UUID, create_command_code(command))
            await client.write_gatt_char(WRITE_UUID, request)
            frame = await _wait_status(statuses)
        return frame
    finally:
        if client is not None:
            try:
                await client.disconnect()
            except Exception:  # noqa: BLE001 - the connection is gone either way
                _LOGGER.debug("Error while disconnecting from %s", address, exc_info=True)
