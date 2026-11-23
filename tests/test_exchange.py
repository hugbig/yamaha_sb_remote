"""ble_connect.async_exchange against the fake soundbar."""

import time

import pytest
from bleak import BleakError

from custom_components.yamaha_sb_remote.ble_connect import (
    SoundbarNotFound,
    SoundbarTimeout,
    async_exchange,
)
from tests.conftest import MAC
from tests.fake_soundbar import build_status_frame

REQUEST = bytes.fromhex("ccaa020305f6")
SUB_UP = bytes.fromhex("ccaa0340784cf9")
LED_DIM_EVENT = bytes.fromhex("ccaa022401d9")


async def test_exchange_returns_status(hass, fake_bar):
    assert await async_exchange(hass, MAC) == build_status_frame(fake_bar.state)
    assert fake_bar.written == [REQUEST]
    assert fake_bar.disconnect_calls == 1


async def test_exchange_sends_commands_then_rereads(hass, fake_bar):
    frame = await async_exchange(hass, MAC, [["subUp"], ["subUp"]])

    assert fake_bar.written == [REQUEST, SUB_UP, SUB_UP, REQUEST]
    assert frame[9] == 24
    assert fake_bar.disconnect_calls == 1


async def test_exchange_not_found(hass, fake_bar):
    fake_bar.reachable = False

    with pytest.raises(SoundbarNotFound):
        await async_exchange(hass, MAC)
    assert fake_bar.written == []


async def test_exchange_timeout(hass, fake_bar):
    fake_bar.answer_status = False

    start = time.monotonic()
    with pytest.raises(SoundbarTimeout):
        await async_exchange(hass, MAC)
    assert time.monotonic() - start < 1
    assert fake_bar.disconnect_calls == 1


async def test_exchange_bleak_error(hass, fake_bar):
    fake_bar.connect_error = BleakError("boom")

    with pytest.raises(BleakError):
        await async_exchange(hass, MAC)


async def test_exchange_ignores_event_frames(hass, fake_bar):
    fake_bar.events_before_status = [b"", LED_DIM_EVENT]

    assert await async_exchange(hass, MAC) == build_status_frame(fake_bar.state)
