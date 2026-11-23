"""Setting up a config entry."""

import logging

from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers import entity_registry as er

from custom_components.yamaha_sb_remote import DOMAIN  # noqa: F401  (import before hass loads)
from tests.conftest import refresh, setup_integration

SUFFIXES = {"mediaplayer", "clear_voice", "bass_ext", "subwoofer", "led"}


async def test_setup_creates_five_entities(hass, config_entry, fake_bar):
    await setup_integration(hass, config_entry)

    unique_ids = {
        entry.unique_id
        for entry in er.async_entries_for_config_entry(er.async_get(hass), config_entry.entry_id)
    }
    assert unique_ids == {f"{config_entry.entry_id}_{suffix}" for suffix in SUFFIXES}


async def test_setup_when_bar_unreachable(hass, config_entry, fake_bar, caplog):
    fake_bar.reachable = False

    ids = await setup_integration(hass, config_entry)
    for entity_id in ids.values():
        await refresh(hass, entity_id)

    assert all(ids.values())
    assert fake_bar.written == []
    assert "BLE device not found" in caplog.text
    assert [r for r in caplog.records if r.levelno >= logging.ERROR] == []
    assert hass.states.get(ids["subwoofer"]).state == STATE_UNKNOWN
    assert hass.states.get(ids["led"]).state == STATE_UNKNOWN
