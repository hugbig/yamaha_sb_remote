"""Protocol tests: command encoding, checksums and status frame decoding."""

from types import SimpleNamespace

import pytest

from custom_components.yamaha_sb_remote.utils import (
    checksum_byte,
    checksum_make,
    create_command_code,
    interpret_message,
    set_by_hex,
)
from tests.fake_soundbar import SoundbarState, build_status_frame

# Status frame captured on a real SR-C20A on 2026-11-23: on, Analog, volume 0x17,
# subwoofer +2, Movie, Clear Voice and Bass Extension on, LED off.
REAL_FRAME = bytes.fromhex("ccaa0e0500110c0017182020000103240237")
REQUEST = bytes.fromhex("ccaa020305f6")


def decode(frame: bytes, entity_type: str) -> SimpleNamespace:
    device = SimpleNamespace(_type=entity_type)
    set_by_hex(int.from_bytes(frame, "big"), device)
    return device


def test_command_power_on():
    assert create_command_code(["powerOn"]) == bytes.fromhex("ccaa0340787ec7")


def test_command_request():
    assert create_command_code(["request"]) == REQUEST


def test_command_volume_set():
    assert create_command_code(["volumeSet", 30]) == bytes.fromhex("ccaa02411e9f")


def test_command_unknown_sends_request():
    assert create_command_code(["nope"]) == REQUEST


def test_checksum_accepts_zero():
    # 0x02 + 0x41 + 0xBD == 0x100, so the checksum byte is 0x00.
    assert checksum_make(bytearray([0x02, 0x41, 0xBD])) == 0
    assert checksum_byte(bytes.fromhex("ccaa0241bd00")) is True


def test_fake_frame_checksum_valid():
    assert checksum_byte(build_status_frame(SoundbarState())) is True


def test_fake_frame_matches_real_capture():
    state = SoundbarState(
        power=True,
        source=0x0C,
        volume=0x17,
        sub=0x18,
        style=0x03,
        clear_voice=True,
        bass_ext=True,
        led=2,
    )
    assert build_status_frame(state) == REAL_FRAME


def test_set_by_hex_real_frame():
    device = decode(REAL_FRAME, "media_player")
    assert device._power is True
    assert device._current_source == "Analog"
    assert device._sound_mode == "Movie"


def test_set_by_hex_media_player():
    frame = build_status_frame(
        SoundbarState(power=True, source=0x05, muted=True, volume=30, style=0x03)
    )
    device = decode(frame, "media_player")
    assert device._power is True
    assert device._current_source == "Bluetooth"
    assert device._muted is True
    assert device._volume == pytest.approx(30 * 1.666 / 100)
    assert device._sound_mode == "Movie"
    assert device._status == "init"


@pytest.mark.parametrize(
    ("entity_type", "state", "attribute", "expected"),
    [
        ("clear_voice", SoundbarState(clear_voice=True), "_power", True),
        ("clear_voice", SoundbarState(bass_ext=True), "_power", False),
        ("bass_ext", SoundbarState(bass_ext=True), "_power", True),
        ("bass_ext", SoundbarState(clear_voice=True), "_power", False),
        ("subwoofer", SoundbarState(sub=24), "_sub", 2),
        ("led", SoundbarState(led=1), "_led", "Dim"),
    ],
)
def test_set_by_hex_switches_number_select(entity_type, state, attribute, expected):
    device = decode(build_status_frame(state), entity_type)
    assert getattr(device, attribute) == expected


def test_interpret_message_power():
    assert interpret_message(bytes.fromhex("ccaa021011cc")) == "Power ON"
