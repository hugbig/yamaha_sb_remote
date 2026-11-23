"""Media player entity."""

import pytest
from homeassistant.const import STATE_OFF, STATE_ON

from tests.conftest import refresh, setup_integration


@pytest.fixture
async def player(hass, config_entry, fake_bar):
    fake_bar.state.power = True
    fake_bar.state.source = 0x05
    entity_id = (await setup_integration(hass, config_entry))["media_player"]
    await refresh(hass, entity_id)
    fake_bar.entity_id = entity_id
    return fake_bar


async def call(hass, player, service, **data):
    await hass.services.async_call(
        "media_player", service, {"entity_id": player.entity_id, **data}, blocking=True
    )


async def test_initial_read(hass, player):
    state = hass.states.get(player.entity_id)
    assert state.state == STATE_ON
    assert state.attributes["source"] == "Bluetooth"


async def test_turn_off_and_on(hass, player):
    await call(hass, player, "turn_off")
    assert player.state.power is False
    assert hass.states.get(player.entity_id).state == STATE_OFF

    await call(hass, player, "turn_on")
    assert player.state.power is True
    assert hass.states.get(player.entity_id).state == STATE_ON


async def test_select_source(hass, player):
    await call(hass, player, "select_source", source="Optical")
    assert player.state.source == 0x0A
    assert hass.states.get(player.entity_id).attributes["source"] == "Optical"


async def test_mute(hass, player):
    await call(hass, player, "volume_mute", is_volume_muted=True)
    assert player.state.muted is True
    assert hass.states.get(player.entity_id).attributes["is_volume_muted"] is True


async def test_select_sound_mode(hass, player):
    await call(hass, player, "select_sound_mode", sound_mode="Game")
    assert player.state.style == 0x0C
    assert hass.states.get(player.entity_id).attributes["sound_mode"] == "Game"


async def test_volume_set(hass, player):
    await call(hass, player, "volume_set", volume_level=0.5)
    # media_player.py sends int(0.5 * 100 / 1.666) == 30
    assert player.state.volume == 30
    assert hass.states.get(player.entity_id).attributes["volume_level"] == 0.5
