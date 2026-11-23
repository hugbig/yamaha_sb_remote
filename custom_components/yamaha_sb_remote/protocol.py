"""Decoding of the soundbar's status frame."""

from dataclasses import dataclass
import logging

from .utils import checksum_byte

_LOGGER = logging.getLogger(__name__)

STATUS_HEADER = bytes([0xCC, 0xAA, 0x0E, 0x05])
STATUS_LENGTH = 18

SOURCES = {0x05: "Bluetooth", 0x07: "TV", 0x0A: "Optical", 0x0C: "Analog"}
SOUND_MODES = {0x03: "Movie", 0x0A: "Standard", 0x0C: "Game"}
SUBWOOFER = {code: level for level, code in zip(range(-4, 5), range(0, 33, 4))}
LEDS = {0: "Bright", 1: "Dim", 2: "Off"}

VOLUME_FACTOR = 1.666 / 100


@dataclass(frozen=True)
class SoundbarState:
    """The soundbar state, as reported by its status frame."""

    power: bool
    source: str | None
    muted: bool
    volume: float
    sound_mode: str | None
    clear_voice: bool
    bass_ext: bool
    subwoofer: int | None
    led: str | None


def is_status_frame(frame: bytes) -> bool:
    """True for an 18-byte frame that starts like a status frame."""
    return len(frame) == STATUS_LENGTH and frame[:4] == STATUS_HEADER


def _lookup(table: dict, value: int, field: str):
    if value not in table:
        _LOGGER.warning("Unknown %s value 0x%02x in status frame", field, value)
        return None
    return table[value]


def parse_status(frame: bytes) -> SoundbarState:
    """Decode a status frame. Raise ValueError if it is not a valid status frame."""
    frame = bytes(frame)
    if not is_status_frame(frame):
        raise ValueError(f"Not a status frame: {frame.hex()}")
    if not checksum_byte(frame):
        raise ValueError(f"Bad checksum in status frame: {frame.hex()}")
    return SoundbarState(
        power=bool(frame[5] & 1),
        source=_lookup(SOURCES, frame[6], "source"),
        muted=bool(frame[7] & 1),
        volume=frame[8] * VOLUME_FACTOR,
        sound_mode=_lookup(SOUND_MODES, frame[14], "sound mode"),
        clear_voice=bool(frame[15] & 0x04),
        bass_ext=bool(frame[15] & 0x20),
        subwoofer=_lookup(SUBWOOFER, frame[9], "subwoofer"),
        led=_lookup(LEDS, frame[16] & 0x03, "LED"),
    )
