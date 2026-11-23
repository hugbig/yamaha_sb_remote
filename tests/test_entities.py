"""Behaviour shared by all entities."""

import pytest
from homeassistant.const import STATE_ON, STATE_UNAVAILABLE
from homeassistant.exceptions import HomeAssistantError

from tests.conftest import setup_integration
from tests.fake_soundbar import SoundbarState, build_status_frame


async def test_entity_names(hass, config_entry, fake_bar):
    ids = await setup_integration(hass, config_entry)

    assert ids == {
        "media_player": "media_player.yamaha_sr_c20a",
        "clear_voice": "switch.yamaha_sr_c20a_clear_voice",
        "bass_ext": "switch.yamaha_sr_c20a_bass_extension",
        "subwoofer": "number.yamaha_sr_c20a_subwoofer",
        "led": "select.yamaha_sr_c20a_led",
    }
    assert hass.states.get(ids["media_player"]).name == "Yamaha SR-C20A"
    assert hass.states.get(ids["clear_voice"]).name == "Yamaha SR-C20A Clear Voice"
    assert hass.states.get(ids["led"]).name == "Yamaha SR-C20A LED"


async def test_command_updates_all_entities(hass, config_entry, fake_bar):
    ids = await setup_integration(hass, config_entry)
    fake_bar.state.clear_voice = True  # changed with the Yamaha remote meanwhile

    await hass.services.async_call(
        "select", "select_option", {"entity_id": ids["led"], "option": "Dim"}, blocking=True
    )

    assert hass.states.get(ids["led"]).state == "Dim"
    assert hass.states.get(ids["clear_voice"]).state == STATE_ON


async def test_command_when_unreachable_raises(hass, config_entry, fake_bar):
    ids = await setup_integration(hass, config_entry)
    fake_bar.reachable = False

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "select", "select_option", {"entity_id": ids["led"], "option": "Off"}, blocking=True
        )
    await hass.async_block_till_done(wait_background_tasks=True)

    # Nothing was sent; the refresh that follows fails too, so the entity becomes unavailable.
    assert fake_bar.state.led == 0
    assert hass.states.get(ids["led"]).state == STATE_UNAVAILABLE


async def test_unknown_source_shows_none(hass, config_entry, fake_bar, caplog):
    fake_bar.frame_override = build_status_frame(SoundbarState(power=True, source=0x99))

    ids = await setup_integration(hass, config_entry)

    state = hass.states.get(ids["media_player"])
    assert state.state == STATE_ON
    assert state.attributes.get("source") is None
    assert "Unknown source value 0x99" in caplog.text


async def test_lost_confirmation_triggers_refresh(hass, config_entry, fake_bar):
    ids = await setup_integration(hass, config_entry)
    fake_bar.answer_after_commands = False

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "select", "select_option", {"entity_id": ids["led"], "option": "Off"}, blocking=True
        )
    await hass.async_block_till_done(wait_background_tasks=True)

    # The command reached the soundbar: a refresh reads the new state back.
    assert fake_bar.state.led == 2
    assert hass.states.get(ids["led"]).state == "Off"


async def test_select_unknown_source_raises(hass, config_entry, fake_bar):
    ids = await setup_integration(hass, config_entry)
    written = len(fake_bar.written)

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "media_player",
            "select_source",
            {"entity_id": ids["media_player"], "source": "Radio"},
            blocking=True,
        )
    assert len(fake_bar.written) == written
