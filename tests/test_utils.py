"""Command encoding, checksums, and the fake soundbar's frame encoder."""

from custom_components.yamaha_sb_remote.utils import (
    checksum_byte,
    checksum_make,
    create_command_code,
    interpret_message,
)
from tests.fake_soundbar import SoundbarState, build_status_frame

# Status frame captured on a real SR-C20A on 2026-11-23: on, Analog, volume 0x17,
# subwoofer +2, Movie, Clear Voice and Bass Extension on, LED off.
REAL_FRAME = bytes.fromhex("ccaa0e0500110c0017182020000103240237")
REQUEST = bytes.fromhex("ccaa020305f6")


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


def test_interpret_message_power():
    assert interpret_message(bytes.fromhex("ccaa021011cc")) == "Power ON"
