"""BleData.callDevice against the fake soundbar."""

import time
from types import SimpleNamespace

import pytest
from bleak import BleakError

from custom_components.yamaha_sb_remote.ble_connect import BleData
from tests.conftest import MAC
from tests.fake_soundbar import SoundbarState, build_status_frame

POWER_ON = bytes.fromhex("ccaa0340787ec7")
REQUEST = bytes.fromhex("ccaa020305f6")


def media_player():
    return SimpleNamespace(_type="media_player", _status="unint")


async def test_status_read_updates_device(hass, fake_bar):
    fake_bar.state.power = True
    device = media_player()

    await BleData(device, hass, MAC).callDevice()

    assert device._status == "init"
    assert device._power is True
    assert fake_bar.disconnect_calls == 1


async def test_command_sent_after_status(hass, fake_bar):
    await BleData(media_player(), hass, MAC).callDevice(["powerOn"])

    assert fake_bar.written == [REQUEST, POWER_ON]
    assert fake_bar.state.power is True


async def test_device_not_found_skips(hass, fake_bar):
    fake_bar.reachable = False

    await BleData(media_player(), hass, MAC).callDevice(["powerOn"])

    assert fake_bar.written == []


async def test_status_timeout_gives_up(hass, fake_bar):
    fake_bar.answer_status = False
    device = media_player()

    start = time.monotonic()
    await BleData(device, hass, MAC).callDevice(["powerOn"])

    assert time.monotonic() - start < 1
    assert device._status == "unint"
    assert fake_bar.written == [REQUEST]
    assert fake_bar.disconnect_calls == 1


async def test_connect_error_is_logged(hass, fake_bar, caplog):
    fake_bar.connect_error = BleakError("boom")

    await BleData(media_player(), hass, MAC).callDevice()

    assert "BLE operation failed" in caplog.text


@pytest.fixture
def loop_errors(hass):
    """Collect exceptions raised in event loop callbacks instead of failing the test."""
    errors = []
    previous = hass.loop.get_exception_handler()
    hass.loop.set_exception_handler(lambda loop, context: errors.append(context))
    yield errors
    hass.loop.set_exception_handler(previous)


async def test_unknown_source_byte_does_not_hang(hass, fake_bar, loop_errors, caplog):
    fake_bar.frame_override = build_status_frame(SoundbarState(source=0x99))
    device = media_player()

    await BleData(device, hass, MAC).callDevice(["powerOn"])

    # The status frame was taken into account (no wait until the timeout) and the command sent.
    assert device._status == "init"
    assert "Timeout waiting for status" not in caplog.text
    assert fake_bar.written == [REQUEST, POWER_ON]


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="an unknown status byte raises KeyError in the notification callback, fixed in lot 3",
)
async def test_unknown_source_byte_is_handled(hass, fake_bar, loop_errors):
    fake_bar.frame_override = build_status_frame(SoundbarState(source=0x99))

    await BleData(media_player(), hass, MAC).callDevice()

    assert loop_errors == []
