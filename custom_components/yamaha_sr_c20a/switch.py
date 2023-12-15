from .ble_connect import BleData

from custom_components.yamaha_sr_c20a import _LOGGER, DOMAIN as SOUNDBAR_DOMAIN
from homeassistant.components.switch import (
    SwitchEntity,
)

import homeassistant.helpers.config_validation as cv

from homeassistant.const import (
    STATE_ON,
    STATE_OFF
)

SWITCH_LIST = [ "clear_voice", "bass_ext"]

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up platform."""
    """Initialize the Soundbar device."""
    devices = []
    soundbar_list = hass.data[SOUNDBAR_DOMAIN]

    for device in soundbar_list:
        _LOGGER.debug("Configured a new SoundbarSwitch %s", device.name)
        for switch in SWITCH_LIST:
            devices.append(SoundbarSwitch(hass, device, switch))
    async_add_entities(devices)


class SoundbarSwitch(SwitchEntity):
    def __init__(self, hass, DeviceEntity, switch):
        self._state = STATE_OFF
        self._type = switch
        self.hass = hass
        self._macAdress = DeviceEntity.macAdress
        self._device_id = DeviceEntity.device_id
        self._name = DeviceEntity.name + '_' + switch
        self._pollingAuto = DeviceEntity.pollingAuto
        self._power = None
        self._status = 'unint'

    # Run when added to HASS TO LOAD SOURCES
    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()


    async def async_update(self):
        """Update the switch State."""
        if self._status == 'unint' or self._pollingAuto is True : 
            ble_connect = BleData(self, self.hass, self._macAdress)
            await ble_connect.callDevice()
            if self._status == 'init' :
                if (self._power == True) :
                    self._state = STATE_ON
                else :
                    self._state = STATE_OFF 

    async def async_turn_on(self):
        ble_connect = BleData(self, self.hass, self._macAdress)
        if self._type == "clear_voice":
            await ble_connect.callDevice(["clearVoiceOn"])
        else:
            await ble_connect.callDevice(["bassOn"])
        self._state = STATE_ON  
        self.isOn = STATE_ON 

    async def async_turn_off(self):
        ble_connect = BleData(self, self.hass, self._macAdress)
        if self._type == "clear_voice":
            await ble_connect.callDevice(["clearVoiceOff"])
        else:
            await ble_connect.callDevice(["bassOff"])
        self._state = STATE_OFF
        self.isOn = STATE_OFF

    @property
    def name(self):
        return self._name


    @property
    def type(self):
        return self._type
    
    @property
    def state(self):
        return self._state

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._device_id + "_" + self._type     