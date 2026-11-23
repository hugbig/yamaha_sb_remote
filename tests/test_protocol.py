"""Pure decoding of the status frame."""

import pytest

from custom_components.yamaha_sb_remote.protocol import SoundbarState, parse_status
from tests.fake_soundbar import SoundbarState as BarState
from tests.fake_soundbar import build_status_frame

REAL_FRAME = bytes.fromhex("ccaa0e0500110c0017182020000103240237")


def test_parse_real_frame():
    state = parse_status(REAL_FRAME)
    assert isinstance(state, SoundbarState)
    assert state.power is True
    assert state.source == "Analog"
    assert state.muted is False
    assert state.volume == pytest.approx(0x17 * 1.666 / 100)
    assert state.sound_mode == "Movie"
    assert state.clear_voice is True
    assert state.bass_ext is True
    assert state.subwoofer == 2
    assert state.led == "Off"


def test_parse_standby():
    state = parse_status(build_status_frame(BarState(power=False, muted=True)))
    assert state.power is False
    assert state.muted is True


def test_parse_unknown_source_is_none(caplog):
    state = parse_status(build_status_frame(BarState(source=0x99, led=1)))
    assert state.source is None
    assert state.led == "Dim"
    assert state.sound_mode == "Standard"
    assert "0x99" in caplog.text


def test_parse_rejects_bad_checksum():
    with pytest.raises(ValueError):
        parse_status(REAL_FRAME[:-1] + b"\x00")


def test_parse_rejects_short_frame():
    with pytest.raises(ValueError):
        parse_status(bytes.fromhex("ccaa022401d9"))
