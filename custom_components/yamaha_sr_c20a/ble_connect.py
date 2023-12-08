import asyncio
from bleak import BleakScanner, BleakClient
import logging
from homeassistant.components import bluetooth
from .utils import *

_LOGGER = logging.getLogger(__name__)

class BleData:
    def __init__(self, device, hass, macAdress):
        self.hass = hass
        self.macAdress = macAdress
        self.device = device

    def handle_data(self,handle, value):
        _LOGGER.info("Received data: %s" % (value.hex()))
        if (len(value) > 3):
            length = value[2]
            if (value[0] != 0xcc):
                _LOGGER.warning("Bad first bit: 0x%s" % (value.hex()))
            elif (value[1] != 0xaa):
                _LOGGER.warning("Bad second bit: 0x%s" % (value.hex()))
            elif not checksum_byte(value):
                _LOGGER.warning("Bad checksum in data: 0x%s" % (value.hex()))
            elif (len(value) - 4 != length):
                _LOGGER.warning("Bad value for data length: 0x%s" % (value.hex()))
            else:
                
                if (length == 14): #this should be a status message
                    self.device = set_by_hex((int(value.hex(), 16)), self.device)
                elif (length == 2):
                    _LOGGER.info("Received: " + interpret_message(value))
                elif (length == 3):
                    _LOGGER.info("Received: " + interpret_message(value))
                elif (length == 5):
                    _LOGGER.info("Received: " + interpret_message(value))
                else:
                    _LOGGER.warning("Received unexpected data length: 0x%s" % (value.hex()))
        elif value.hex() == "":
            _LOGGER.info("Received empty data packet, this is expected once on startup")
        else:
            _LOGGER.warning("Received data that is not an expected message size: 0x%s" % (value.hex()))
        if (handle != 0x8): _LOGGER.info("Bad handle: %s" % str(handle))
    


    async def callDevice(self, command = None):
        request = create_command_code(['request'], self.device)
        bleDevice = bluetooth.async_ble_device_from_address(self.hass, self.macAdress, connectable=True)
        async with BleakClient(bleDevice) as adapter:
            await adapter.start_notify('5cafe9de-e7b0-4e0b-8fb9-2da91a7ae3ed', self.handle_data)
            await adapter.write_gatt_char("0c50e7fa-594c-408b-ae0d-b53b884b7c08",request)  
            while self.device._status == 'unint' :
                _LOGGER.debug("WAIT FOR notify handle : " + self.device._status)
                await asyncio.sleep(0.06)
            if command == None :
                return
            else: 
                _LOGGER.warning("COMMAND " + command[0])
                code = create_command_code(command, self.device)
                await adapter.write_gatt_char("0c50e7fa-594c-408b-ae0d-b53b884b7c08",code)
                await asyncio.sleep(0.1)