from custom_components.yamaha_sb_remote import (
    _LOGGER,
    DEVICE_MANUFACTURER,
    DOMAIN as SOUNDBAR_DOMAIN,
)

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.const import CONF_NAME, STATE_OFF, STATE_ON
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .ble_connect import BleData

DEVICE_SOURCE_TYPE = ["Bluetooth", "TV", "Optical", "Analog"]

DEVICE_SOURCE_MODE = ["Standard", "Movie", "Game"]


class YamahaMediaPlayer(MediaPlayerEntity):
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

    def __init__(self, hass, config):
        _LOGGER.info("Initializing Yamaha mediaplayer")
        self.hass = hass
        self._macAdress = config.data["mac_adress"]
        self._device_id = config.entry_id
        self._name = config.data[CONF_NAME]
        self._service_name = config.data[CONF_NAME]
        self._pollingAuto = config.data["polling_auto"]
        self._state = STATE_OFF
        self._status = "unint"
        self._type = "media_player"
        self._power = None
        self._current_source = None
        self._volume = 0
        self._sound_mode = None
        self._muted = False

    # Run when added to HASS TO LOAD SOURCES
    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def device_id(self):
        return self._device_id

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._device_id + "_mediaplayer"

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

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(SOUNDBAR_DOMAIN, self._device_id)},
            name=self._service_name,
            manufacturer=DEVICE_MANUFACTURER,
            model=SOUNDBAR_DOMAIN,
        )

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
        self._volume = (newVolume * 1.666) / 100

    async def async_volume_down(self) -> None:
        """Volume up the media player."""
        newVolume = int((self._volume * 100) / 1.666) - 5
        ble_connect = BleData(self, self.hass, self._macAdress)
        command = ["volumeSet", newVolume]
        ble_connect = BleData(self, self.hass, self._macAdress)
        await ble_connect.callDevice(command)
        self._volume = (newVolume * 1.666) / 100

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

    async def async_update(self):
        """Update the media player State."""
        _LOGGER.debug("Call update on %s", self._name)
        if self._status == "unint" or self._pollingAuto is True:
            ble_connect = BleData(self, self.hass, self._macAdress)
            await ble_connect.callDevice()
            if self._status == "init":
                if self._power is True:
                    self._state = STATE_ON
                else:
                    self._state = STATE_OFF


async def async_setup_entry(hass, config, async_add_entities):
    async_add_entities([YamahaMediaPlayer(hass, config)])
