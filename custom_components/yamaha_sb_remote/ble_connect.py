import asyncio
from bleak import BleakClient, BleakError
from bleak_retry_connector import establish_connection
import logging
from homeassistant.components import bluetooth
from .utils import *

_LOGGER = logging.getLogger(__name__)


CONNECTION_LOCK = asyncio.Lock()

NOTIFY_UUID = "5cafe9de-e7b0-4e0b-8fb9-2da91a7ae3ed"
WRITE_UUID = "0c50e7fa-594c-408b-ae0d-b53b884b7c08"
STATUS_TIMEOUT = 5.0


class BleData:
    def __init__(self, device, hass, macAdress):
        self.hass = hass
        self.macAdress = macAdress
        self.device = device

    def handle_data(self, characteristic, value):
        _LOGGER.info("Received data: %s", value.hex())
        if len(value) > 3:
            length = value[2]
            if value[0] != 0xcc:
                _LOGGER.warning("Bad first bit: 0x%s", value.hex())
            elif value[1] != 0xaa:
                _LOGGER.warning("Bad second bit: 0x%s", value.hex())
            elif not checksum_byte(value):
                _LOGGER.warning("Bad checksum in data: 0x%s", value.hex())
            elif len(value) - 4 != length:
                _LOGGER.warning("Bad value for data length: 0x%s", value.hex())
            elif length == 14:
                self.device = set_by_hex(int(value.hex(), 16), self.device)
            elif length in (2, 3, 5):
                _LOGGER.info("Received: %s", interpret_message(value))
            else:
                _LOGGER.warning("Received unexpected data length: 0x%s", value.hex())
        elif value.hex() == "":
            _LOGGER.info("Received empty data packet, this is expected once on startup")
        else:
            _LOGGER.warning("Received data that is not an expected message size: 0x%s", value.hex())

    async def callDevice(self, command=None):
        request = create_command_code(['request'], self.device)
        bleDevice = bluetooth.async_ble_device_from_address(self.hass, self.macAdress, connectable=True)
        if bleDevice is None:
            _LOGGER.warning("BLE device not found for address %s, skipping", self.macAdress)
            return
        async with CONNECTION_LOCK:
            client = None
            try:
                client = await establish_connection(
                    BleakClient,
                    bleDevice,
                    bleDevice.address,
                )
                await client.start_notify(NOTIFY_UUID, self.handle_data)
                await client.write_gatt_char(WRITE_UUID, request)
                elapsed = 0.0
                while self.device._status == "unint":
                    _LOGGER.debug("WAIT FOR notify handle: %s", self.device._status)
                    await asyncio.sleep(0.06)
                    elapsed += 0.06
                    if elapsed >= STATUS_TIMEOUT:
                        _LOGGER.error(
                            "Timeout waiting for status notification from %s",
                            self.macAdress,
                        )
                        return
                if command is None:
                    return
                _LOGGER.debug("COMMAND %s", command[0])
                code = create_command_code(command, self.device)
                await client.write_gatt_char(WRITE_UUID, code)
                await asyncio.sleep(0.1)
            except BleakError as e:
                _LOGGER.error("BLE operation failed: %s", e)
            except Exception as e:
                _LOGGER.error("Unexpected error: %r", e)
            finally:
                if client is not None:
                    try:
                        await client.disconnect()
                    except Exception:
                        pass
