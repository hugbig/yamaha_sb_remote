"""Media player entity."""

import pytest
from homeassistant.const import STATE_OFF, STATE_ON

from tests.conftest import setup_integration


@pytest.fixture
async def player(hass, config_entry, fake_bar):
    fake_bar.state.power = True
    fake_bar.state.source = 0x05
    fake_bar.entity_id = (await setup_integration(hass, config_entry))["media_player"]
    return fake_bar


async def call(hass, player, service, **data):
    await hass.services.async_call(
        "media_player", service, {"entity_id": player.entity_id, **data}, blocking=True
    )


def attributes(hass, player):
    return hass.states.get(player.entity_id).attributes


async def test_initial_read(hass, player):
    assert hass.states.get(player.entity_id).state == STATE_ON
    assert attributes(hass, player)["source"] == "Bluetooth"


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
    assert attributes(hass, player)["source"] == "Optical"


async def test_mute(hass, player):
    await call(hass, player, "volume_mute", is_volume_muted=True)
    assert player.state.muted is True
    assert attributes(hass, player)["is_volume_muted"] is True


async def test_select_sound_mode(hass, player):
    await call(hass, player, "select_sound_mode", sound_mode="Game")
    assert player.state.style == 0x0C
    assert attributes(hass, player)["sound_mode"] == "Game"


async def test_volume_set(hass, player):
    await call(hass, player, "volume_set", volume_level=0.5)
    # int(0.5 * 100 / 1.666) == 30, read back as 30 * 1.666 / 100
    assert player.state.volume == 30
    assert attributes(hass, player)["volume_level"] == pytest.approx(30 * 1.666 / 100)


async def test_volume_up(hass, player):
    await call(hass, player, "volume_up")
    assert player.state.volume == 25
