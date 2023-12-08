#import urllib.parse
#import async_timeout
#import aiohttp
import asyncio
#import re
import logging
import voluptuous as vol
import homeassistant.util as util
from datetime import timedelta
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .ble_connect import BleData

_LOGGER = logging.getLogger(__name__)


from homeassistant.components.media_player import (
  MediaPlayerEntity,
  MediaPlayerEntityFeature,
  MediaPlayerDeviceClass,
  PLATFORM_SCHEMA
)


VERSION = '0.1.0'
DOMAIN = "yamaha_sr_c20a"

from homeassistant.const import (
  CONF_NAME,
  STATE_ON,
  STATE_OFF,
  CONF_SCAN_INTERVAL
)

DEVICE_SOURCE_TYPE = [
  'Bluetooth',
  'TV',
  'Optical',
  'Analog'
]

DEVICE_SOURCE_MODE = [
  'Standard',
  'Movie',
  'Game'
]

DEFAULT_NAME = 'Yamaha SR-C20A'
SCAN_INTERVAL = timedelta(seconds=5)
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=3)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=3)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
  vol.Required("mac_adress", default='XX:XX:XX:XX'): cv.string,
  vol.Optional("polling_auto", default=False): cv.boolean,
  vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
  vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period
})


class YamahaDevice(MediaPlayerEntity):
  """Representation of the device."""
  _attr_supported_features = (
    MediaPlayerEntityFeature.SELECT_SOUND_MODE
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.SELECT_SOURCE
  )
  _attr_device_class = MediaPlayerDeviceClass.SPEAKER
  _attr_has_entity_name = True
  _attr_name = None


  def __init__(self, name, hass, macAdress, pollingAuto = False):
    _LOGGER.info('Initializing YamahaDevice')
    self.hass = hass
    self._macAdress = macAdress
    self._name = name
    self._state = STATE_OFF
    self._status = 'unint'
    self._power = None
    self._current_source = None
    self._volume = 0
    self._sound_mode = None
    self._muted = False
    self._pollingAuto = pollingAuto

  @property
  def name(self):
    """Return the name of the device."""
    return self._name

  @property
  def state(self):
    """Return the state of the device."""
    return self._state

  @property
  def unique_id(self) -> str:
    """Return the unique ID of the sensor."""
    return "62ad47ad-fddb-4d27-b3e8-68494e78ca03"  

  @property
  def sound_mode(self):
    """Return the sub mode of the device."""
    return self._sound_mode

  @property
  def volume_level(self):
    """Return the volume level."""
    return self._volume

  @property
  def source(self):
    """Return the current source."""
    return self._current_source

  @property
  def source_list(self):
    """List of available input sources."""
    return sorted(DEVICE_SOURCE_TYPE)

  @property
  def sound_mode_list(self):
    """List of available mode."""
    return sorted(DEVICE_SOURCE_MODE) 

  @property
  def is_volume_muted(self):
    """Boolean if volume is currently muted."""
    return self._muted     

  async def async_set_volume_level(self, volume):
    """Sets the volume level."""
    newVolume = int((volume * 100) / 1.666)
    command = ["volumeSet", newVolume]
    ble_connect = BleData(self, self.hass, self._macAdress)
    await ble_connect.callDevice(command)
    self._volume = volume


  async def async_volume_up(self) -> None:
    """Volume up the media player."""
    newVolume = int((self._volume * 100) / 1.666) + 5
    ble_connect = BleData(self, self.hass, self._macAdress)
    command = ["volumeSet", newVolume]
    ble_connect = BleData(self, self.hass, self._macAdress)
    await ble_connect.callDevice(command)
    self._volume =  (newVolume * 1.666) / 100

  async def async_volume_down(self) -> None:
    """Volume up the media player."""
    newVolume = int((self._volume * 100) / 1.666) - 5
    ble_connect = BleData(self, self.hass, self._macAdress)
    command = ["volumeSet", newVolume]
    ble_connect = BleData(self, self.hass, self._macAdress)
    await ble_connect.callDevice(command)
    self._volume =  (newVolume * 1.666) / 100

  async def async_mute_volume(self, mute):
    """Sets volume mute to true."""
    ble_connect = BleData(self, self.hass, self._macAdress)
    if mute:
      await ble_connect.callDevice(["muteOn"])
    else:
      await ble_connect.callDevice(["muteOff"])
    self._muted = mute

  async def async_select_sound_mode(self, sound_mode):
    """Switch the sound mode of the entity."""  
    if sound_mode not in DEVICE_SOURCE_MODE:
      _LOGGER.error("Unsupported mode")
      return
    ble_connect = BleData(self, self.hass, self._macAdress)
    await ble_connect.callDevice([sound_mode])
    self._sound_mode = sound_mode

  async def async_select_source(self, source):
    """Select input source."""
    if source not in DEVICE_SOURCE_TYPE:
      _LOGGER.error("Unsupported source")
      return
    ble_connect = BleData(self, self.hass, self._macAdress)
    await ble_connect.callDevice([source])
    self._current_source = source

  async def async_turn_off(self):
    """Turn the media player off."""
    self._state = STATE_OFF
    ble_connect = BleData(self, self.hass, self._macAdress)
    await ble_connect.callDevice(["powerOff"])
    

  async def async_turn_on(self):
    """Turn the media player on."""
    self._state = STATE_ON
    ble_connect = BleData(self, self.hass, self._macAdress)
    await ble_connect.callDevice(["powerOn"])
    

  #@util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_FORCED_SCANS)
  async def async_update(self):
    """Update the media player State."""
    _LOGGER.warning("Polling Auto " + str(self._pollingAuto))
    if self._status == 'unint' or self._pollingAuto == True : 
      ble_connect = BleData(self, self.hass, self._macAdress)
      await ble_connect.callDevice()
      if self._status == 'init' :
        if (self._power == True) :
          self._state = STATE_ON
        else :
          self._state = STATE_OFF 

def setup_platform(hass, config, add_devices, discovery_info=None):
  """Set up the Samsung MultiRoom platform."""
  macAdress = config.get('mac_adress')
  pollingAuto = config.get('polling_auto')
  name = config.get(CONF_NAME)
  session = async_get_clientsession(hass)
  add_devices([YamahaDevice(name, hass, macAdress, pollingAuto)])