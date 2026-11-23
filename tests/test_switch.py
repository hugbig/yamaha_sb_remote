"""Clear Voice and Bass Extension switches."""

import pytest
from homeassistant.const import STATE_OFF, STATE_ON

from tests.conftest import setup_integration


@pytest.fixture
async def ids(hass, config_entry, fake_bar):
    fake_bar.state.clear_voice = True
    return await setup_integration(hass, config_entry)


async def test_initial_read(hass, ids):
    assert hass.states.get(ids["clear_voice"]).state == STATE_ON
    assert hass.states.get(ids["bass_ext"]).state == STATE_OFF


@pytest.mark.parametrize("key", ["clear_voice", "bass_ext"])
async def test_turn_off_and_on(hass, ids, fake_bar, key):
    entity_id = ids[key]

    await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id}, blocking=True)
    assert getattr(fake_bar.state, key) is False
    assert hass.states.get(entity_id).state == STATE_OFF

    await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
    assert getattr(fake_bar.state, key) is True
    assert hass.states.get(entity_id).state == STATE_ON
