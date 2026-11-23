"""Subwoofer number."""

import pytest
from homeassistant.exceptions import HomeAssistantError

from tests.conftest import setup_integration
from tests.fake_soundbar import SoundbarState as BarState
from tests.fake_soundbar import build_status_frame

REQUEST = bytes.fromhex("ccaa020305f6")
SUB_UP = bytes.fromhex("ccaa0340784cf9")


async def set_value(hass, entity_id, value):
    await hass.services.async_call(
        "number", "set_value", {"entity_id": entity_id, "value": value}, blocking=True
    )


async def test_initial_read(hass, config_entry, fake_bar):
    entity_id = (await setup_integration(hass, config_entry))["subwoofer"]
    assert float(hass.states.get(entity_id).state) == 0


async def test_set_value_one_connection(hass, config_entry, fake_bar):
    entity_id = (await setup_integration(hass, config_entry))["subwoofer"]
    written, disconnects = len(fake_bar.written), fake_bar.disconnect_calls

    await set_value(hass, entity_id, 3)

    assert fake_bar.written[written:] == [REQUEST, SUB_UP, SUB_UP, SUB_UP, REQUEST]
    assert fake_bar.disconnect_calls == disconnects + 1
    assert fake_bar.state.sub == 28
    assert float(hass.states.get(entity_id).state) == 3


async def test_set_same_value_sends_nothing(hass, config_entry, fake_bar):
    entity_id = (await setup_integration(hass, config_entry))["subwoofer"]
    written = len(fake_bar.written)

    await set_value(hass, entity_id, 0)

    assert len(fake_bar.written) == written


async def test_set_value_uses_fresh_level(hass, config_entry, fake_bar):
    entity_id = (await setup_integration(hass, config_entry))["subwoofer"]
    fake_bar.state.sub = 24  # changed to +2 with the Yamaha remote; the cache still says 0
    written = len(fake_bar.written)

    await set_value(hass, entity_id, 3)

    assert fake_bar.written[written:] == [REQUEST, SUB_UP, REQUEST]
    assert float(hass.states.get(entity_id).state) == 3


async def test_set_value_unknown_level_raises(hass, config_entry, fake_bar):
    fake_bar.frame_override = build_status_frame(BarState(sub=0x02))  # not a known level
    entity_id = (await setup_integration(hass, config_entry))["subwoofer"]

    with pytest.raises(HomeAssistantError):
        await set_value(hass, entity_id, 1)
    assert SUB_UP not in fake_bar.written
