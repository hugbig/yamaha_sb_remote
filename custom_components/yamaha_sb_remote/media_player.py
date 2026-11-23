"""Media player: power, source, volume, mute and sound mode."""

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)

from homeassistant.exceptions import ServiceValidationError

from .entity import YamahaEntity
from .protocol import SOUND_MODES, SOURCES, VOLUME_FACTOR

# Displayed name -> command name in utils.create_command_code
SOURCE_COMMANDS = {"Bluetooth": "Bluetooth", "TV": "TV", "Optical": "Optical", "Analog": "Analog"}
SOUND_MODE_COMMANDS = {"Standard": "Standard", "Movie": "Movie", "Game": "Game"}
assert set(SOURCE_COMMANDS) == set(SOURCES.values())
assert set(SOUND_MODE_COMMANDS) == set(SOUND_MODES.values())

VOLUME_STEP = 5  # raw volume units


class YamahaMediaPlayer(YamahaEntity, MediaPlayerEntity):
    """The soundbar as a media player."""

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
    _attr_name = None
    _attr_source_list = sorted(SOURCES.values())
    _attr_sound_mode_list = sorted(SOUND_MODES.values())

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "mediaplayer")

    @property
    def state(self) -> MediaPlayerState:
        return MediaPlayerState.ON if self.coordinator.data.power else MediaPlayerState.OFF

    @property
    def source(self) -> str | None:
        return self.coordinator.data.source

    @property
    def sound_mode(self) -> str | None:
        return self.coordinator.data.sound_mode

    @property
    def volume_level(self) -> float:
        return self.coordinator.data.volume

    @property
    def is_volume_muted(self) -> bool:
        return self.coordinator.data.muted

    def _raw_volume(self) -> int:
        return round(self.coordinator.data.volume / VOLUME_FACTOR)

    async def async_turn_on(self) -> None:
        await self._send(["powerOn"])

    async def async_turn_off(self) -> None:
        await self._send(["powerOff"])

    async def async_select_source(self, source: str) -> None:
        if source not in SOURCE_COMMANDS:
            raise ServiceValidationError(f"Unknown source: {source}")
        await self._send([SOURCE_COMMANDS[source]])

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        if sound_mode not in SOUND_MODE_COMMANDS:
            raise ServiceValidationError(f"Unknown sound mode: {sound_mode}")
        await self._send([SOUND_MODE_COMMANDS[sound_mode]])

    async def async_mute_volume(self, mute: bool) -> None:
        await self._send(["muteOn" if mute else "muteOff"])

    async def async_set_volume_level(self, volume: float) -> None:
        await self._send(["volumeSet", int(volume / VOLUME_FACTOR)])

    async def async_volume_up(self) -> None:
        await self._send(["volumeSet", self._raw_volume() + VOLUME_STEP])

    async def async_volume_down(self) -> None:
        await self._send(["volumeSet", max(self._raw_volume() - VOLUME_STEP, 0)])


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([YamahaMediaPlayer(entry.runtime_data)])
